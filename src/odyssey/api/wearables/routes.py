import base64
import logging
import secrets

from datetime import datetime, date, time, timedelta, timezone

import boto3
import dateutil
import requests

from boto3.dynamodb.conditions import Key
from flask import current_app, jsonify, request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from flask_pymongo import ASCENDING, DESCENDING
from requests_oauthlib import OAuth2Session
from sqlalchemy.sql import text
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db, mongo
from odyssey.api.wearables.models import *
from odyssey.api.wearables.schemas import *
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.constants import WEARABLE_DATA_DEFAULT_RANGE_DAYS, WEARABLE_DEVICE_TYPES
from odyssey.utils.json import JSONProvider
from odyssey.utils.misc import check_client_existence, date_validator, lru_cache_with_ttl, iso_string_to_iso_datetime

logger = logging.getLogger(__name__)

#########################
#
# V1 of the Wearables API
#
#########################

ns = Namespace('wearables', description='Endpoints for registering wearable devices.')

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesEndpoint(BaseResource):
    @token_auth.login_required(user_type=('client','staff'), resources=('wearable_data',))
    @responds(schema=WearablesSchema, status_code=200, api=ns)
    def get(self, user_id):
        """ Wearable device information for client ``user_id`` in response to a GET request.

        This endpoint returns information on which wearables a client has. For
        each supported wearable device, two keys exist in the returned dictionary:
        ``has_<device_name>`` to indicate whether or not the client has this device,
        and ``registered_<device_name>`` to indicate whether or not the registration
        of the wearable device with Modo Bio was completed successfully.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        wearables = (
            Wearables.query
            .filter_by(user_id=user_id)
            .one_or_none())

        return wearables

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=WearablesSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Create new wearables information for client ``user_id`` in reponse to a POST request.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=WearablesSchema, api=ns)
    @responds(status_code=204, api=ns)
    def put(self, user_id):
        """ Update wearables information for client ``user_id`` in reponse to a PUT request.

        Parameters
        ----------
        user_id : int
            User ID number.
        """
        query = Wearables.query.filter_by(user_id=user_id)
        data = WearablesSchema().dump(request.parsed_obj)
        query.update(data)
        db.session.commit()


@ns.route('/oura/auth/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesOuraAuthEndpoint(BaseResource):
    @token_auth.login_required(user_type=('client',))
    @responds(schema=WearablesOAuthGetSchema, status_code=200, api=ns)
    def get(self, user_id):
        """ Oura OAuth2 parameters to initialize the access grant process.

        Use these parameters to initiate the OAuth2 access grant process with
        Oura. You must replace the value for ``redirect_uri`` with a
        valid redirect URI. The redirect URI must match the URI registered
        with Oura.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict containing:
            - url
            - client_id
            - redirect_uri (must be replaced with actual URI)
            - response_type (literal word 'code')
            - state
            - scope (space separated string of scopes)
        """
        info = Wearables.query.filter_by(user_id=user_id).one_or_none()
        if not info:
            raise BadRequest(
                f'user_id {user_id} not found in Wearables table. '
                f'Connect to POST /wearables first.')

        state = secrets.token_urlsafe(24)

        # Store state in database
        oura = (
            WearablesOura.query
            .filter_by(user_id=user_id)
            .one_or_none())

        if not oura:
            oura = WearablesOura(user_id=user_id, oauth_state=state, wearable_id=info.idx)
            db.session.add(oura)
        else:
            oura.oauth_state = state
        db.session.commit()

        url = current_app.config['OURA_AUTH_URL']
        client_id = current_app.config['OURA_CLIENT_ID']
        scope = current_app.config['OURA_SCOPE']

        return {
            'url': url,
            'client_id': client_id,
            'redirect_uri': 'replace-this',
            'response_type': 'code',
            'scope': scope,
            'state': state}

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=WearablesOAuthPostSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Oura OAuth2 access grant code exchange.

        Post OAuth2 parameters here after user clicks 'allow' on the Oura homepage.
        This endpoint will reach out to Oura for the second part of the OAuth2
        process, exchanging the grant code for an access token and a refresh token.

        Parameters
        ----------
        code : str
            Access grant code.

        state : str
            State code, must be the same code as received from `GET /wearables/oura/auth`.

        redirect_uri : str
            The redirect URI used to come back to the frontend app after the user clicked
            'allow' on the Oura homepage. Must be registered with Oura.

        scope : str
            The scopes the user actually selected when clicking 'allow'. Space separated
            string of scopes. Required for Oura.
        """
        oura = WearablesOura.query.filter_by(user_id=user_id).one_or_none()
        if not oura:
            raise BadRequest(
                f'user_id {user_id} not found in WearablesOura table. '
                f'Connect to GET /wearables/oura/auth first.')

        if request.parsed_obj['state'] != oura.oauth_state:
            raise BadRequest('OAuth state changed between requests.')

        # Oura ring returns selected scope with redirect.
        # Not requiring email or personal
        minimal_scope = set(current_app.config['OURA_SCOPE'].split())
        scope = set(request.parsed_obj.get('scope', '').split())

        if scope.intersection(minimal_scope) != minimal_scope:
            msg = 'You must agree to share at least: {}.'.format(', '.join(minimal_scope))
            raise BadRequest(msg)

        # Exchange access grant code for access token
        client_id = current_app.config['OURA_CLIENT_ID']
        client_secret = current_app.config['OURA_CLIENT_SECRET']
        token_url = current_app.config['OURA_TOKEN_URL']

        oauth_session = OAuth2Session(
            client_id,
            state=request.parsed_obj['state'],
            redirect_uri=request.parsed_obj['redirect_uri'])
        try:
            oauth_reply = oauth_session.fetch_token(
                token_url,
                code=request.parsed_obj['code'],
                include_client_id=True,
                client_secret=client_secret)
        except Exception as e:
            raise BadRequest(f'Error while exchanging grant code for access token: {e}')

        # Everything was successful
        oura.access_token = oauth_reply['access_token']
        oura.refresh_token = oauth_reply['refresh_token']
        oura.token_expires = datetime.utcnow() + timedelta(seconds=oauth_reply['expires_in'])
        oura.oauth_state = None
        oura.wearable.has_oura = True
        oura.wearable.registered_oura = True

        db.session.commit()

    @token_auth.login_required(user_type=('client',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """ Revoke Oura OAuth2 data sharing permissions.

        Parameters
        ----------
        user_id : str
            Modo Bio user ID.
        """
        oura = (
            WearablesOura.query
            .filter_by(user_id=user_id)
            .one_or_none())

        if oura:
            oura.access_token = None
            oura.refresh_token = None
            oura.wearable.registered_oura = False
            db.session.commit()


@ns.route('/fitbit/auth/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesFitbitAuthEndpoint(BaseResource):
    @token_auth.login_required(user_type=('client',))
    @responds(schema=WearablesOAuthGetSchema, status_code=200, api=ns)
    def get(self, user_id):
        """ Fitbit OAuth2 parameters to initialize the access grant process.

        Use these parameters to initiate the OAuth2 access grant process with
        Fitbit. You must replace the value for ``redirect_uri`` with a
        valid redirect URI. The redirect URI must match the URI registered
        with Fitbit.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict containing:
            - url
            - client_id
            - redirect_uri (must be replaced with actual URI)
            - response_type (literal word 'code')
            - state
            - scope (space separated string of scopes)
        """
        info = Wearables.query.filter_by(user_id=user_id).one_or_none()
        if not info:
            raise BadRequest(
                f'user_id {user_id} not found in Wearables table. '
                f'Connect to POST /wearables first.')

        state = secrets.token_urlsafe(24)

        # Store state in database
        fitbit = (
            WearablesFitbit.query
            .filter_by(user_id=user_id)
            .one_or_none())

        if not fitbit:
            fitbit = WearablesFitbit(user_id=user_id, oauth_state=state, wearable_id=info.idx)
            db.session.add(fitbit)
        else:
            fitbit.oauth_state = state
        db.session.commit()

        url = current_app.config['FITBIT_AUTH_URL']
        client_id = current_app.config['FITBIT_CLIENT_ID']
        scope = current_app.config['FITBIT_SCOPE']

        return {
            'url': url,
            'client_id': client_id,
            'redirect_uri': 'replace-this',
            'response_type': 'code',
            'scope': scope,
            'state': state}

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=WearablesOAuthPostSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Fitbit OAuth2 access grant code exchange.

        Post OAuth2 parameters here after user clicks 'allow' on the Fitbit homepage.
        This endpoint will reach out to Fitbit for the second part of the OAuth2
        process, exchanging the grant code for an access token and a refresh token.

        Parameters
        ----------
        code : str
            Access grant code.

        state : str
            State code, must be the same code as received from `GET /wearables/fitbit/auth`.

        redirect_uri : str
            The redirect URI used to come back to the frontend app after the user clicked
            'allow' on the Fitbit homepage. Must be registered with Fitbit.

        scope : str
            The scopes the user actually selected when clicking 'allow'. Space separated
            string of scopes. Ignored for Fitbit.
        """
        fitbit = WearablesFitbit.query.filter_by(user_id=user_id).one_or_none()
        if not fitbit:
            raise BadRequest(
                f'user_id {user_id} not found in WearablesFitbit table. '
                f'Connect to GET /wearables/fitbit/auth first.')

        if request.parsed_obj['state'] != fitbit.oauth_state:
            raise BadRequest('OAuth state changed between requests.')

        # Exchange access grant code for access token
        client_id = current_app.config['FITBIT_CLIENT_ID']
        client_secret = current_app.config['FITBIT_CLIENT_SECRET']
        token_url = current_app.config['FITBIT_TOKEN_URL']

        # Fitbit requires client ID and client secret as basic auth in header.
        auth_str = base64.urlsafe_b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')

        oauth_session = OAuth2Session(
            client_id,
            state=request.parsed_obj['state'],
            redirect_uri=request.parsed_obj['redirect_uri'])
        try:
            oauth_reply = oauth_session.fetch_token(
                token_url,
                code=request.parsed_obj['code'],
                include_client_id=True,
                client_secret=client_secret,
                headers = {'Authorization': f'Basic {auth_str}'})
        except Exception as e:
            raise BadRequest(f'Error while exchanging grant code for access token: {e}')

        # Fitbit sends errors in body with a 200 response.
        if not oauth_reply.get('success', True):
            msg = oauth_reply['errors'][0]['message']
            raise BadRequest(f'fitbit.com returned error: {msg}')

        # Not requiring location, settings, or social
        minimal_scope = set(current_app.config['FITBIT_SCOPE'].split())
        scope = set(oauth_reply.get('scope', []))

        if scope.intersection(minimal_scope) != minimal_scope:
            msg = 'You must agree to share at least: {}.'.format(', '.join(minimal_scope))
            raise BadRequest(msg)

        # Everything was successful
        fitbit.access_token = oauth_reply['access_token']
        fitbit.refresh_token = oauth_reply['refresh_token']
        fitbit.token_expires = datetime.utcnow() + timedelta(seconds=oauth_reply['expires_in'])
        fitbit.oauth_state = None
        fitbit.wearable.has_fitbit = True
        fitbit.wearable.registered_fitbit = True

        db.session.commit()

    @token_auth.login_required(user_type=('client',))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """ Revoke Fitbit OAuth2 data sharing permissions.

        Parameters
        ----------
        user_id : str
            Modo Bio user ID.
        """
        fitbit = (
            WearablesFitbit.query
            .filter_by(user_id=user_id)
            .one_or_none())

        if fitbit:
            fitbit.access_token = None
            fitbit.refresh_token = None
            fitbit.wearable.registered_fitbit = False
            db.session.commit()


@ns.route('/freestyle/activate/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesFreeStyleActivateEndpoint(BaseResource):
    @token_auth.login_required(user_type=('client',))
    @responds(schema=WearablesFreeStyleActivateSchema, status_code=200, api=ns)
    def get(self, user_id):
        """ Returns CGM activation timestamp for client ``user_id`` in reponse to a GET request.

        Time data on the CGM sensor is stored as minutes since activation and as full
        timestamps in the database. Time data must be converted before it can be
        uploaded to the database, using the activation timestamp retrieved in this GET
        request.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        str
            JSON encoded, ISO 8601 formatted datetime string.
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(user_id=user_id)
            .one_or_none())

        return cgm

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=WearablesFreeStyleActivateSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Set new activation timestamp for client ``user_id`` in response to POST request.

        When a new CGM is activated, the activation timestamp must be stored in the database.

        Parameters
        ----------
        user_id : int
            User ID number.

        timestamp : str
            ISO 8601 formatted datetime string.
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(user_id=user_id)
            .one_or_none())

        if not cgm:
            info = Wearables.query.filter_by(user_id=user_id).one_or_none()
            if not info:
                info = Wearables(user_id=user_id)
                db.session.add(info)
                db.session.flush()

            cgm = WearablesFreeStyle(user_id=user_id, wearable_id=info.idx, wearable=info)
            db.session.add(cgm)

        cgm.activation_timestamp = request.parsed_obj.activation_timestamp
        cgm.wearable.has_freestyle = True
        cgm.wearable.registered_freestyle = True
        db.session.commit()


@ns.route('/freestyle/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesFreeStyleEndpoint(BaseResource):
    @token_auth.login_required(user_type=('client',))
    @responds(schema=WearablesFreeStyleSchema, status_code=200, api=ns)
    def get(self, user_id):
        """ Return FreeStyle CGM data for client ``user_id`` in reponse to a GET request.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        str
            JSON encoded dictionary
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(user_id=user_id)
            .one_or_none())

        return cgm

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=WearablesFreeStyleSchema, api=ns)
    @responds(status_code=204, api=ns)
    def patch(self, user_id):
        """ Add CGM data for client ``user_id`` in reponse to a PATCH request.

        Parameters
        ----------
        user_id : int
            User ID number.
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(user_id=user_id)
            .one_or_none())

        if not cgm:
            msg =  f'FreeStyle Libre for client {user_id} has not yet been activated. '
            msg += f'Send a POST request to /wearables/freestyle/activate/ first.'
            raise BadRequest(msg)

        if cgm.activation_timestamp != request.parsed_obj.activation_timestamp:
            msg =  f'Activation timestamp {request.parsed_obj.activation_timestamp} does not '
            msg += f'match current activation timestamp {cgm.activation_timestamp}. '
            msg += f'Send a GET request to /wearables/freestyle/activate/ first.'
            raise BadRequest(msg)

        tstamps = request.parsed_obj.timestamps
        glucose = request.parsed_obj.glucose

        if len(tstamps) != len(glucose):
            raise BadRequest('Data arrays not equal length.')

        if not tstamps:
            return

        if len(tstamps) != len(set(tstamps)):
            raise BadRequest('Duplicate timestamps in data.')

        # Sort data
        if tstamps != sorted(tstamps):
            temp = sorted(zip(tstamps, glucose))
            tstamps = []
            glucose = []
            for t, g in temp:
                tstamps.append(t)
                glucose.append(g)

        # Find index where new data starts
        n = 0
        if cgm.timestamps:
            while n < len(tstamps) and tstamps[n] <= cgm.timestamps[-1]:
                n += 1

        # No new data
        if n == len(tstamps):
            return

        # Use array concatenation here, don't use:
        #    cgm.glucose = cgm.glucose + request.parsed_obj.glucose
        # See ... confluence page
        stmt = text('''
            UPDATE "WearablesFreeStyle"
            SET glucose = glucose || cast(:gluc as double precision[]),
                timestamps = timestamps || cast(:tstamps as timestamp without time zone[])
            WHERE user_id = :cid;
        ''').bindparams(
            gluc=glucose[n:],
            tstamps=tstamps[n:],
            cid=user_id)
        db.session.execute(stmt)
        db.session.commit()


@ns.route('/data/<string:device_type>/<int:user_id>/')
@ns.doc(params={
    'user_id': 'User ID number',
    'device_type': 'fitbit, applewatch, oura, freestyle',
    'start_date': '(optional) iso formatted date. start of date range',
    'end_date': '(optional) iso formatted date. end of date range'
    })
class WearablesData(BaseResource):
    @token_auth.login_required(user_type=('client','staff'), resources=('wearable_data',))
    @responds(status_code=200, api=ns)
    def get(self, user_id, device_type):
        """ Retrieve wearables data from dynamodb.

        Parameters
        ----------
        user_id : int
            User ID number

        device_type : str
            only the data from one device per request.

        Returns
        -------
        dict
            The requested wearables data.
        """

        # connect to dynamo
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(current_app.config['WEARABLES_DYNAMO_TABLE'])

        # validate device_type request
        if device_type not in WEARABLE_DEVICE_TYPES:
            raise BadRequest(f"wearable device type, {device_type}, not supported")

        # configure date range expression
        # Four cases:
        #   - both start and end date provided: return data for date range
        #   - only start date specified: return start_date + WEARABLE_DATA_DEFAULT_RANGE_DAYS
        #   - only end date specified: return end_date - WEARABLE_DATA_DEFAULT_RANGE_DAYS
        #   - no dates specified: return last WEARABLE_DATA_DEFAULT_RANGE_DAYS days of data
        start_date = date_validator(request.values.get('start_date')) if request.values.get('start_date') else None
        end_date =  date_validator(request.values.get('end_date')) if request.values.get('end_date') else None
        if start_date and end_date:
            date_condition = Key('date').between(start_date, end_date)
        elif start_date:
            end_date = (datetime.fromisoformat(start_date) + timedelta(days=WEARABLE_DATA_DEFAULT_RANGE_DAYS)).date().isoformat()
            date_condition = Key('date').between(start_date, end_date)
        elif end_date:
            start_date = (datetime.fromisoformat(end_date) - timedelta(days=WEARABLE_DATA_DEFAULT_RANGE_DAYS)).date().isoformat()
            date_condition = Key('date').between(start_date, end_date)
        else:
            start_date = (datetime.now() - timedelta(days=WEARABLE_DATA_DEFAULT_RANGE_DAYS)).date().isoformat()
            end_date = datetime.now().date().isoformat()
            date_condition =  Key('date').gte(start_date)

        # make reqeust for data
        response = table.query(
            KeyConditionExpression= Key('user_id').eq(user_id) & date_condition,
            FilterExpression = Key('wearable').eq(device_type))

        payload = {'start_date': start_date, 'end_date': end_date, 'total_items': len(response.get('Items', [])), 'items': []}

        # only provide the data that is required
        payload['items'] = response.get('Items', [])

        return jsonify(payload)


#########################
#
# V2 of the Wearables API
#
#########################

# V2 is the terra integration. It is namespaced into v2, which will eventually be
# the v2/ prefix for the entire API once we reach v2.0.0. Once that is reached,
# fold this v2 into that.
#

import enum
import requests
import terra

from terra.api.api_responses import (
    HOOK_TYPES,
    HOOK_RESPONSE,
    USER_DATATYPES,
    TerraApiResponse,
    ConnectionErrorHookResponse,
    RequestProcessingHookResponse,
    RequestCompletedHookResponse)

ns_v2 = Namespace(
    'wearables',
    description='Endpoints for registering wearable devices.')

# Fix mistakes in terra-python wrappers:
# - misspelled connexion_error instead of connection_error (v0.0.7)
# - request_processing was replaced by large_request_processing (v0.0.7)
# - request_completed was replaced by large_request_sending (v0.0.7)
# - permission_change is undocumented, seems come be in response to scope change (v0.0.7)
HOOK_TYPES.add('connection_error')
HOOK_RESPONSE['connection_error'] = ConnectionErrorHookResponse

HOOK_TYPES.add('large_request_processing')
HOOK_RESPONSE['large_request_processing'] = RequestProcessingHookResponse

HOOK_TYPES.add('large_request_sending')
HOOK_RESPONSE['large_request_sending'] = RequestCompletedHookResponse

HOOK_TYPES.add('permission_change')

MIDNIGHT = time(0)
ONE_WEEK = timedelta(weeks=1)
WAY_BACK_WHEN = datetime(2010, 1, 1)

WEBHOOK_RESPONSES = HOOK_TYPES.copy()
WEBHOOK_RESPONSES.update(set(USER_DATATYPES))


class TerraClient(terra.Terra):
    """ Subclass of :class:`terra.Terra` with extra response handling functions.

    Terra uses different names for variables than we do in our API. Below is a
    mapping of variable names.

    =============  ============
    Modo Bio       Terra
    =============  ============
    user_id        reference_id
    terra_user_id  user_id
    wearable       provider
    =============  ============
    """

    def __init__(
        self,
        terra_api_key: str = None,
        terra_dev_id: str = None,
        terra_api_secret: str = None
    ):
        """ Initialize :class:``TerraClient``.

        The connection with Terra requires 3 tokens: the API key, the
        API secret, and a developer ID. By default they are taken from
        the app config. Provide any of them as kwargs to override the
        environmental variables.

        Parameters
        ----------
        terra_api_key : str, default = None
            Override the value taken from TERRA_API_KEY.

        terra_dev_id : str, default = None
            Override the value taken from TERRA_DEV_ID.

        terra_api_secret : str, default = None
            Override the value taken from TERRA_API_SECRET.
        """
        if terra_api_key is None:
            terra_api_key = current_app.config['TERRA_API_KEY']
        if terra_dev_id is None:
            terra_dev_id = current_app.config['TERRA_DEV_ID']
        if terra_api_secret is None:
            terra_api_secret = current_app.config['TERRA_API_SECRET']
        super().__init__(terra_api_key, terra_dev_id, terra_api_secret)

    def status(self, response: TerraApiResponse, raise_on_error: bool=True):
        """ Handles various response status messages from Terra.

        If status is:

        - **success** or **processing** the message is logged at debug level.
        - **warning** the message is logged at warning level.
        - **error** or **not_available** an error is raised.
        - anything else or missing, an error is raised.

        No error is raised if ``raise_on_error`` is False. Instead, the error
        is logged at error level.

        The response object is not consumed or altered; nothing is returned.

        Parameters
        ----------
        response : :class:`terra.api.api_responses.TerraApiResponse`
            Any subclass of :class:`terra.api.api_responses.TerraApiResponse`.

        raise_on_error : bool, default = True
            Whether or not to raise a :class:`werkzeug.exceptions.BadRequest` on error.

        Raises
        ------
        :class:`werkzeug.exceptions.BadRequest`
            Raised when ``status`` is error, not available, or an unknown response. Only
            raised if ``raise_on_error`` is True (default).
        """
        if 'status' not in response.json:
            if 'data' in response.json:
                # Data messages in webhook do not (always?) have a status message.
                return
            elif raise_on_error:
                raise BadRequest(f'Terra returned a response without a status.')
            logger.error(f'Terra response without a status: {response.json}')
            return

        status = response.json['status']

        if status in ('error', 'not_available'):
            msg = response.json.get('message', 'no error message provided')
            if raise_on_error:
                raise BadRequest(f'Terra error: {msg}')
            logger.error(f'Terra balked: {msg}')
        elif status == 'warning':
            msg = response.json.get('message', 'no warning message provided')
            logger.warn(f'Terra complained: {msg}')
        elif status in ('success', 'processing'):
            logger.debug(f'Terra proclaimed: {response.json}')
        else:
            logger.error(f'Unknown status "{status}" in Terra response: {response.json}')
            if raise_on_error:
                raise BadRequest(f'Terra returned an unknown response.')

    def auth_response(self, response: TerraApiResponse):
        """ Handle authentication and reauthentication webhook responses.

        This function is called by the webhook in response to user authentication or
        reauthentication messages. It adds a new user + wearable combination to the WearablesV2
        table in the database, or updates an existing user + wearable combo. It then fetches
        historical data for the user and finally logs an audit message.

        Parameters
        ----------
        response : :class:`terra.api.api_responses.TerraApiResponse`
            The repsonse object returned from :func:`terra.Terra.handle_flask_webhook`.
        """
        user_id = response.parsed_response.reference_id
        wearable = response.parsed_response.user.provider
        terra_user = response.parsed_response.user
        terra_user_id = response.parsed_response.user.user_id

        user_wearable = db.session.get(WearablesV2, (user_id, wearable))

        if not user_wearable:
            # New user
            user_wearable = WearablesV2(
                user_id=user_id,
                wearable=wearable,
                terra_user_id=terra_user_id)
            db.session.add(user_wearable)
            db.session.commit()

            logger.audit(
                f'User {user_id} successfully registered wearable '
                f'device {wearable} (Terra ID {terra_user_id})')

            # Fetch historical data. Data is send to webhook.
            now = datetime.utcnow()

            # The incoming Terra "User" class is converted to an object,
            # but it is not connected to the client (here: self).
            terra_user._client = self

            response = self.get_activity_for_user(terra_user, WAY_BACK_WHEN, end_date=now)
            self.status(response, raise_on_error=False)

            # We already have biographical info.
            # response = self.get_athlete_for_user(terra_user, WAY_BACK_WHEN, end_date=now)
            # self.status(response, raise_on_error=False)

            response = self.get_body_for_user(terra_user, WAY_BACK_WHEN, end_date=now)
            self.status(response, raise_on_error=False)

            response = self.get_daily_for_user(terra_user, WAY_BACK_WHEN, end_date=now)
            self.status(response, raise_on_error=False)

            response = self.get_menstruation_for_user(terra_user, WAY_BACK_WHEN, end_date=now)
            self.status(response, raise_on_error=False)

            response = self.get_nutrition_for_user(terra_user, WAY_BACK_WHEN, end_date=now)
            self.status(response, raise_on_error=False)

            response = self.get_sleep_for_user(terra_user, WAY_BACK_WHEN, end_date=now)
            self.status(response, raise_on_error=False)

        elif user_wearable.terra_user_id != terra_user_id:
            # User reauthentication
            user_wearable.terra_user_id = terra_user_id
            db.session.commit()

            logger.audit(
                f'User {user_id} reauthenticated wearable device {wearable} '
                f'(new Terra ID {terra_user_id})')

    def access_revoked_response(self, response: TerraApiResponse):
        """ Handle deauthentication webhook responses.

        This function is called by the webhook in response to user deauthentication messages.
        The user can revoke access in three ways:

        1.  Through our API. This case is handled by the DELETE v2/wearables/<user_id>/<wearable>
            endpoint.
        2.  Through the wearable provider AND the provider informs Terra. In this case Terra
            will send a deauthentication message to the webhook.
        3.  Through the wearable provider and the provider does NOT inform Terra. Eventually,
            Terra will try to fetch data from the now blocked account, which will fail. Terra
            then sends a connection error message to the webhook.

        This function handles situations 2 and 3. In both cases, the user + wearable combination
        will be deleted from the database and all wearable data will be erased. An audit message
        is logged.

        If the user + wearable combo does not exist in the database, it is silently ignored.

        Parameters
        ----------
        response : :class:`terra.api.api_responses.TerraApiResponse`
            The repsonse object returned from :func:`terra.Terra.handle_flask_webhook`.
        """
        user_id = response.parsed_response.user.reference_id
        wearable = response.parsed_response.user.provider
        terra_user = response.parsed_response.user

        user_wearable = db.session.get(WearablesV2, (user_id, wearable))

        if not user_wearable:
            logger.warn(
                f'Access revoke requested for user_id {user_id} and wearable {wearable}, '
                f'but was not found in the DB. Ignoring.')
            return

        if isinstance(response, ConnectionErrorHookResponse):
            # Request Terra to remove user
            resp = self.deauthenticate_user(terra_user)
            self.status(resp, raise_on_error=False)

        mongo.db.wearables.delete_many({
            'user_id': user_id,
            'wearable': wearable})

        db.session.delete(user_wearable)
        db.session.commit()

        logger.audit(
            f'User {user_id} revoked access to wearable {wearable}. Info and data deleted.')

    def store_data(self, response: TerraApiResponse):
        """ Store incoming data in Mongo.

        Data is stored as::

            { "user_id": 1,
              "wearable": "FITBIT",
              "timestamp": datetime(2022, 10, 12, 4, 0, 0, tz=(None, -28800)),
              "data": {
                  <data_type> (e.g. "activity", "nutrition"): {
                  ...data...
                },
                  <data_type>: {
                  ...data...
                }
              }
            }

        Timestamps are passed in from Terra as data.metadata.start_time. This is converted
        into a timezone-aware datetime object by the JSONProvider class. The "wearables"
        Mongo collection is timezone aware.

        This means that, in order to get all data for one day, you have to search for
        ">= 2022-12-11T00:00:00" and "< 2022-12-13T00:00:00".
        """
        terra_user_id = response.parsed_response.user.user_id
        wearable = response.parsed_response.user.provider
        data_type = response.parsed_response.type

        user_id = (db.session.execute(
            select(WearablesV2.user_id)
            .filter_by(terra_user_id=terra_user_id))
            .scalars()
            .one_or_none())

        if not user_id:
            logger.error(f'User id not found for incoming data for Terra user id {terra_user_id}.')
            return

        # Don't use parsed_response here, want to re-deserialize JSON with our JSONProvider.
        for data in response.get_json()['data']:
            # Update existing or create new doc (upsert).
            result = mongo.db.wearables.update_one(
                {'user_id': user_id, 'wearable': wearable, 'timestamp': data['metadata']['start_time']},
                {'$set': {f'data.{data_type}': data}},
                upsert=True)


@lru_cache_with_ttl(maxsize=1, ttl=86400)
def supported_wearables() -> dict:
    """ Get the list of supported wearables from Terra.

    Terra's API provides a list of supported wearable devices. This function fetches that
    list and caches the result. It is updated once per day.

    The wearable devices are split into two lists, "providers" (web API based devices) and
    "sdk_providers" (SDK based devices). Each entry has an enum name (used in the API) and
    a display name.

    The display names are generated from the enum names, with an exception list for those
    cases where simply lower-casing is not sufficient. By having a "default translation"
    from enum name to display name plus a list of exceptions, any newly supported devices
    returned from Terra's API are automatically included. Exceptions can later be added
    to the list.

    Returns
    -------
    dict
        Dictionary with two keys "providers" and "sdk_providers". The values are dictionaries
        with enum names as keys and display names as values.
    """
    tc = TerraClient()
    response = tc.list_providers()
    tc.status(response, raise_on_error=False)

    # List of display names that cannot be generated by simply capitalizing the enum names.
    exceptions = {
        'APPLE': 'Apple HealthKit',
        'CONCEPT2': 'Concept 2',
        'EIGHT': 'Eight Sleep',
        'FREESTYLELIBRE': 'Freestyle Libre',
        'FREESTYLELIBRESDK': 'Freestyle Libre (SDK)',
        'GOOGLE': 'Google Fit',
        'GOOGLEFIT': 'Google Fit (SDK)',
        'IFIT': 'iFit',
        'TEMPO': 'Tempo Fit',
        'TRAININGPEAKS': 'Training Peaks',
        'WEAROS': 'Wear OS'}

    # These devices are not supported at the moment.
    # That's a business decision, there is no technical reason not to support them.
    # Simply remove them from this list to start supporting them.
    suppressed = {
        'BIOSTRAP',
        'BRYTONSPORT',
        'CARDIOMOOD',
        'CONCEPT2',
        'CRONOMETER',
        'CYCLINGANALYTICS',
        'EATTHISMUCH',
        'EIGHT',
        'FATSECRET',
        'FINALSURGE',
        'GOOGLE',
        'GOOGLEFIT',
        'HAMMERHEAD',
        'HUAWEI',
        'IFIT',
        'INBODY',
        'KETOMOJOEU',
        'KETOMOJOUS',
        'KOMOOT',
        'LEZYNE',
        'LIVEROWING',
        'MOXY',
        'MYFITNESSPAL',
        'NOLIO',
        'NUTRACHECK',
        'PELOTON',
        'PUL',
        'REALTIME',
        'RENPHO',
        'RIDEWITHGPS',
        'ROUVY',
        'SAMSUNG',
        'TECHNOGYM',
        'TEMPO',
        'TODAYSPLAN',
        'TRAINERROAD',
        'TRAININGPEAKS',
        'TRAINXHALE',
        'TRIDOT',
        'UNDERARMOUR',
        'VELOHERO',
        'VIRTUAGYM',
        'WAHOO',
        'WEAROS',
        'WGER',
        'WHOOP',
        'XERT',
        'XOSS',
        'ZWIFT'}

    result = {}
    for provider_type in ('providers', 'sdk_providers'):
        subresult = {}
        for provider in getattr(response.parsed_response, provider_type):
            if provider in suppressed:
                continue
            if provider in exceptions:
                subresult[provider] = exceptions[provider]
            else:
                subresult[provider] = provider.capitalize()
        result[provider_type] = subresult

    return result

def parse_wearable(wearable: str) -> str:
    """ Parse wearable path parameter.

    Clean up path parameter and check against list of supported devices.
    Cleaning up consists of converting to all-caps and removing spaces.

    Parameters
    ----------
    wearable : str
        Name of the wearable.

    Returns
    -------
    str
        Name of the wearable "cleaned up". Cleaning up consists of converting to
        all-caps and removing spaces.

    Raises
    ------
    :class:`werkzeug.exceptions.BadRequest`
        Raised when the wearable (after cleaning up), is not found in the list
        of supported wearable devices, see :func:`supported_wearables`.
    """
    wearable_clean = wearable.upper().replace(' ', '')
    supported = supported_wearables()
    if (wearable_clean in supported['providers']
        or wearable_clean in supported['sdk_providers']):
        return wearable_clean
    raise BadRequest(f'Unknown wearable {wearable}')


@ns_v2.route('')
class WearablesV2Endpoint(BaseResource):
    @token_auth.login_required
    @responds(schema=WearablesV2ProvidersGetSchema, api=ns_v2)
    def get(self):
        """ Get a list of all supported wearable devices. """
        return supported_wearables()


@ns_v2.route('/<int:user_id>')
class WearablesV2UserEndpoint(BaseResource):
    @token_auth.login_required
    @responds(schema=WearablesV2UserGetSchema, status_code=200, api=ns_v2)
    def get(self, user_id):
        """ Get a list of wearable devices registered to this user. """
        # user_id = self.check_user(uid, user_type='client').user_id

        wearables = (db.session.execute(
            select(WearablesV2.wearable)
            .filter_by(user_id=user_id))
            .scalars()
            .all())

        return {'wearables': wearables}


@ns_v2.route('/<int:user_id>/<wearable>')
class WearablesV2DataEndpoint(BaseResource):
    @token_auth.login_required
    # @responds(schema=WearablesV2DataSchema, status_code=200, api=ns_v2)
    def get(self, user_id, wearable):
        """ Get data for this combination of user and wearable device for the default date range. """
        wearable = parse_wearable(wearable)
        today = datetime.utcnow()
        start = today - ONE_WEEK
        data = mongo.db.wearables.find({
            'user_id': user_id,
            'wearable': wearable,
            'timestamp': {'$gte': start}})

        return JSONProvider().dumps(list(data))

    @token_auth.login_required
    @responds(schema=WearablesV2UserAuthUrlSchema, status_code=201, api=ns_v2)
    def post(self, user_id, wearable):
        """ Register a new wearable device for this user. """
        # user_id = self.check_user(uid, user_type='client').user_id
        wearable = parse_wearable(wearable)

        # API based providers
        if wearable in supported_wearables()['providers']:
            # For local testing, set the redirect urls to something like http://localhost/xyz
            # When you copy the URL into a browser and allow access, Terra will redirect back
            # to localhost. It will give an error in the browser, but the URL in the address
            # bar will have all the relevant information.
            tc = TerraClient()
            response = tc.generate_authentication_url(
                resource=wearable,
                auth_success_redirect_url='modobio://wearablesAuthSuccess',
                auth_failure_redirect_url='modobio://wearablesAuthFailure',
                reference_id=user_id)
            tc.status(response)

            # Not stored in the database at this point.
            # Registration is only complete when client follows the link to the provider.
            # The response of that action comes in through the webhook and will be stored.

            return response.parsed_response

        # SDK based providers
        else:
            # Functionality not in terra-python (v0.0.7), use requests.
            url = f'{terra.constants.BASE_URL}/auth/generateAuthToken'
            headers = {
                'accept': 'application/json',
                'dev-id': current_app.config['TERRA_DEV_ID'],
                'x-api-key': current_app.config['TERRA_API_KEY']}

            response = requests.post(url, headers=headers)
            response_json = response.json()

            status = response_json.pop('status', 'error')
            if status != 'success':
                raise BadRequest(f'Terra replied: {response_json}')

            # Same as for API based providers, nothing stored in the database at this point.
            # Registration is only complete when frontend calls initConnection() with token.
            # The response of that action comes in through the webhook and will be stored.

            return response_json

    @token_auth.login_required
    @responds(status_code=204, api=ns_v2)
    def delete(self, user_id, wearable):
        """ Revoke access for this wearable device. """
        # user_id = self.check_user(uid, user_type='client').user_id
        wearable = parse_wearable(wearable)

        user_wearable = db.session.get(WearablesV2, (user_id, wearable))

        # Don't error on non-existant users, delete is idempotent
        if not user_wearable:
            logger.debug(f'Nothing to delete for user {user_id} and wearable {wearable}')
            return

        tc = TerraClient()
        try:
            terra_user = tc.from_user_id(str(user_wearable.terra_user_id))
        except (terra.exceptions.NoUserInfoException, KeyError):
            # Terra-python (at least v0.0.7) should fail with NoUserInfoException
            # if terra_user_id does not exist in their system. However, it checks
            # whether response.json is empty, which is not empty in the case of an
            # error (it holds the error message and status). The next step in
            # terra.models.user.User.fill_in_user_info() is to access
            # response.json["user"] which does not exist and fails with KeyError.
            # In any case, we don't care that the terra_user_id is invalid, we
            # were going to delete it anyway.
            # 2023-01-10: Terra has been notified of this bug.
            pass
        else:
            response = tc.deauthenticate_user(terra_user)
            tc.status(response)

        mongo.db.wearables.delete_many({
            'user_id': user_id,
            'wearable': wearable})

        db.session.delete(user_wearable)
        db.session.commit()
        logger.audit(
            f'User {user_id} revoked access to wearable {wearable}. Info and data deleted.')


@ns_v2.route('/<int:user_id>/<wearable>/<date:start_date>')
@ns_v2.route('/<int:user_id>/<wearable>/<datetime:start_date>')
class WearablesV2DataStartDateEndpoint(BaseResource):
    @token_auth.login_required
    # @responds(schema=WearablesV2DataSchema, status_code=200, api=ns_v2)
    def get(self, user_id, wearable, start_date):
        """ Get data for this combination of user and wearable device from start_date to now.

        Date range includes start date and latest available data. Start_date can be either
        a full ISO8601 datetime, or just the date.
        """
        if isinstance(start_date, date):
            start_date = datetime.combine(start_date, MIDNIGHT)

        wearable = parse_wearable(wearable)
        data = mongo.db.wearables.find({
            'user_id': user_id,
            'wearable': wearable,
            'timestamp': {'$gte': start_date}})

        return JSONProvider().dumps(list(data))


@ns_v2.route('/<int:user_id>/<wearable>/<date:start_date>/<date:end_date>')
@ns_v2.route('/<int:user_id>/<wearable>/<datetime:start_date>/<datetime:end_date>')
class WearablesV2DataStartToEndDateEndpoint(BaseResource):
    @token_auth.login_required
    # @responds(schema=WearablesV2DataSchema, status_code=200, api=ns_v2)
    def get(self, user_id, wearable, start_date, end_date):
        """ Get data for this combination of user and wearable device from start_date to end_date.

        Date range includes boundaries: [start_date, end_date]. Start_date can be either
        a full ISO8601 datetime, or just the date. End_date must be of the same format as
        start_date.
        """
        if isinstance(start_date, date):
            start_date = datetime.combine(start_date, MIDNIGHT)
            end_date = datetime.combine(end_date, MIDNIGHT)

        wearable = parse_wearable(wearable)
        data = mongo.db.wearables.find({
            'user_id': user_id,
            'wearable': wearable,
            'timestamp': {
                '$and': [
                    {'$gte': start_date},
                    {'$lte': end_date}]}})

        return JSONProvider().dumps(list(data))


@ns_v2.route('/terra')
class WearablesV2TerraWebHookEndpoint(BaseResource):
    @accepts(api=ns_v2)
    def post(self):
        """ Webhook for incoming notifications from Terra. """
        # Override JSON handling for this request.
        request.json_module = JSONProvider()

        tc = TerraClient()
        # These two lines do the same thing, but the first checks the signature in the header,
        # which relies on having the secret. For testing without the secret, use the second line.
        response = tc.handle_flask_webhook(request)
        # response = terra.api.api_responses.TerraWebhookResponse(request.get_json(), dtype='hook')

        tc.status(response, raise_on_error=False)

        if response.dtype not in WEBHOOK_RESPONSES:
            logger.error(
                f'Terra webhook response with unknown type "{response.dtype}". '
                f'Full message: {response.json}')
        elif response.dtype == 'auth':
            # Completion of new wearable registration for user,
            # or reauthentication by existing user.
            tc.auth_response(response)
        elif response.dtype == 'user_reauth':
            # Terra sends both auth and user_reauth in response
            # to reauthentication. Only need one, ignore this one.
            pass
        elif response.dtype == 'permission_change':
            # Undocumented response. Seems to be in response to OAuth scope change.
            pass
        elif response.dtype == 'deauth':
            # User revoked access through our API. Nothing else to do.
            pass
        elif response.dtype in ('access_revoked', 'connection_error'):
            # User revoked access through wearable provider.
            tc.access_revoked_response(response)
        elif response.dtype == 'google_no_datasource':
            # uh, ok
            pass
        elif response.dtype in (
            'request_processing',
            'request_completed',
            'large_request_processing',
            'large_request_sending'):
            # Terra is letting us know that they're working on it. Great.
            pass
        elif response.dtype in USER_DATATYPES:
            tc.store_data(response)


@ns_v2.route('/calculations/blood-glucose/<int:user_id>/<string:wearable>')
class WearablesV2BloodGlucoseCalculationEndpoint(BaseResource):
    @token_auth.login_required
    @ns_v2.doc(params={'start_date': 'Start of specified date range. Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)',
                'end_date': 'End of specified date range. Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)'})
    @responds(schema=WearablesV2BloodGlucoseCalculationOutputSchema, status_code=200, api=ns_v2)
    def get(self, user_id, wearable):
        """ Get calculated values related to blood glucose wearable data.

        This route will return all calculated values related to blood glucose data for a particular user_id, wearable, and date range.

        Path Parameters
        ----------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood glucose data

        Query Parameters
        ----------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 7 days if not specified 
        end_date: str
            End of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date if not specified

        Returns
        -------
        dict
            JSON encoded dict containing:
            - user_id
            - average_glucose - mg/dL
            - standard_deviation
            - glucose_management_indicator - percentage
            - glucose_variability - percentage
        """

        wearable = parse_wearable(wearable)

        # Default dates
        today = datetime.utcnow()
        start = today - ONE_WEEK

        start_date = iso_string_to_iso_datetime(request.args.get('start_date')) if request.args.get('start_date') else start
        end_date = iso_string_to_iso_datetime(request.args.get('end_date')) if request.args.get('end_date') else today

        """Calculate Average Glucose"""
        #  Begin with defining each stage of the pipeline

        # Filter documents on user_id, wearable, and date range
        stage_match_user_id_and_wearable = {
            '$match': {
                'user_id': user_id,
                'wearable': wearable,
                'date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
        }

        # Unwind the blood_glucose_samples array so that we can operate on each individual sample
        stage_unwind_blood_glucose_samples = {
            '$unwind': '$data.body.glucose_data.blood_glucose_samples'
        }

        # Group all of these documents together and calculate average glucose and standard deviation for the group
        stage_group_average_and_std_dev = {
            '$group': {
                '_id': None,
                'average_glucose': { 
                    '$avg': '$data.body.glucose_data.blood_glucose_samples.blood_glucose_mg_per_dL'
                    },
                'standard_deviation': {
                    '$stdDevPop': '$data.body.glucose_data.blood_glucose_samples.blood_glucose_mg_per_dL'
                }
            }
        }

        # Add field for GMI and calculate it. Calculated as 3.31 + 0.02392 x (mean glucose in mg/dL) 
        stage_add_gmi = {
            '$addFields': {
                'glucose_management_indicator': { '$add': [{'$multiply': ['$average_glucose', 0.02392]}, 3.31] }
            }
        }

        # Add field for glucose variability and calculate it. Calculated as 100 * (Standard Deviation / Mean Glucose)
        stage_add_glucose_variability = {
            '$addFields': {
                'glucose_variability': { '$multiply': [100, {'$divide': ['$standard_deviation', '$average_glucose']}] }
            }
        }

        # Assemble pipeline
        pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_blood_glucose_samples,
            stage_group_average_and_std_dev,
            stage_add_gmi,
            stage_add_glucose_variability
        ]

        # MongoDB pipelines return a cursor
        cursor = mongo.db.wearables.aggregate(pipeline)
        document_list = list(cursor)
        data = {}

        # We need to grab the document that we want from that cursor so we can format the data in a payload
        if document_list:
            data = document_list[0]

        # Build and return payload
        payload = {
            'user_id': user_id,
            'wearable': wearable,
            'average_glucose': data.get('average_glucose'),
            'standard_deviation': data.get('standard_deviation'),
            'glucose_management_indicator': data.get('glucose_management_indicator'),
            'glucose_variability': data.get('glucose_variability')
        }

        return payload
        

