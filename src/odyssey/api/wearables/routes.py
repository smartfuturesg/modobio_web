import base64
import logging
import secrets

from datetime import datetime, timedelta

import boto3
import requests
import terra

from boto3.dynamodb.conditions import Key
from flask import current_app, jsonify, request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from requests_oauthlib import OAuth2Session
from sqlalchemy.sql import text
from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.wearables.models import (
    Wearables,
    WearablesOura,
    WearablesFitbit,
    WearablesFreeStyle)
from odyssey.api.wearables.schemas import (
    WearablesSchema,
    WearablesOuraAuthSchema,
    WearablesOAuthGetSchema,
    WearablesOAuthPostSchema,
    WearablesFreeStyleSchema,
    WearablesFreeStyleActivateSchema)
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.constants import WEARABLE_DATA_DEFAULT_RANGE_DAYS, WEARABLE_DEVICE_TYPES
from odyssey.utils.misc import check_client_existence, date_validator, lru_cache_with_ttl

logger = logging.getLogger(__name__)

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


##########################################################################################
#
# V2 of the Wearables API
#
# V2 is the terra integration. It is namespaced into v2, which will eventually be
# the v2/ prefix for the entire API once we reach v2.0.0. Once that is reached,
# fold this v2 into that.
#


ns_v2 = Namespace(
    'wearables',
    description='Endpoints for registering wearable devices.')


class TerraClient(terra.Terra):
    def __init__(self):
        super().__init__(
            current_app.config['TERRA_API_KEY'],
            current_app.config['TERRA_DEV_ID'],
            current_app.config['TERRA_API_SECRET'])

    def status(self, response: terra.api.api_responses.TerraApiResponse):
        """ Handles various response status messages from Terra.

        - If status is ``success``, nothing is returned.
        - If status is ``warning``, the warning message is logged.
        - If status is ``error``, :class:`werkzeug.exceptions.BadRequest` is raised.
        - If status is anything else, :class:`werkzeug.exceptions.BadRequest` is raised.
        - If status is not present in the response, nothing is returned.

        In the case of warning or success, the ``status`` keyword is removed from the
        ``response.json`` object. With a warning, the ``message`` key is also removed.

        Parameters
        ----------
        response : :class:`terra.api.api_responses.TerraApiResponse`
            Any subclass of :class:`terra.api.api_responses.TerraApiResponse`.

        Raises
        ------
        :class:`werkzeug.exceptions.BadRequest`
            Raised when ``status`` is error or an unknown response.
        """
        if 'status' not in response.json:
            return

        status = response.json.pop('status')

        if status == 'error':
            msg = response.json.get('message', 'no error message provided')
            raise BadRequest(f'Terra returned: {msg}')
        elif status == 'warning':
            msg = response.json.pop('message', 'no warning message provided')
            logger.warn(f'Terra warned: {msg}')
        elif status == 'success':
            pass
        else:
            logger.error(f'Unknown status "{status}" in Terra response: {response.json}')
            raise BadRequest(f'Terra returned an unknown response.')


    def auth_response(self, response: terra.api.api_responses.TerraApiResponse):
        """ Handle auth webhook response. """
        user_id = response.reference_id
        wearable = response.user.provider
        terra_user_id = response.user.user_id

        user_wearable = (db.session.execute(
            select(WearablesV2)
            .filter_by(
                user_id=user_id,
                wearable=wearable))
            .one_or_none())

        if response.status == 'error':
            # Flow interupted, delete user+wearable entry from DB
            if response.reason == 'auth_cancelled':
                logger.info(f'User {user_id} cancelled wearable {wearable} registration.')
            elif response.reason == 'missing_scopes':
                logger.info(f'User {user_id} did not include requested scopes for {wearable}.')
            else:
                logger.error(
                    f'Wearable device registration for user {user_id} and wearable '
                    f'{wearable} failed for unknown reason: {response.message}')

            # If terra_user_id does not match, ignore. This could happen if
            # user did a re-auth but cancelled half-way.
            if user_wearable and user_wearable.terra_user_id == terra_user_id:
                user_wearable.delete()
                db.session.commit()

        elif response.status == 'success':
            # Registration success
            if not user_wearable:
                # user+wearable not found in DB, ignore.
                logger.warn(
                    f'User {user_id} with wearable {wearable} not found in DB. '
                     'Ignoring registration attempt.')
            elif user_wearable.terra_user_id != terra_user_id:
                # user+wearable found, but terra_user_id mismatch, might be
                # part of re-authentication. Let user_reauth message handle it.
                pass
            else:
                # Success.
                user_wearable.registration_complete = True
                db.session.commit()
                logger.audit(
                    f'User {user_id} successfully registered wearable '
                    f'device {wearable} (Terra ID {terra_user_id})')

                # TODO: fetch data


    def reauth_response(self, response: terra.api.api_responses.TerraApiResponse):
        """ Handle reauth webhook response. """
        user_id = response.reference_id
        wearable = response.user.provider
        old_terra_user_id = response.old_user.user_id
        new_terra_user_id = response.new_user.user_id

        user_wearable = (db.session.execute(
            select(WearablesV2)
            .filter_by(
                user_id=user_id,
                wearable=wearable))
            .one_or_none())

        if not user_wearable:
            logger.warn(
                f'User {user_id} tried to re-authenticate wearable {wearable}, '
                f'but was not found in the DB.')
        elif user_wearable.terra_user_id != old_terra_user_id:
            if user_wearable.terra_user_id == new_terra_user_id:
                # Already updated, do nothing.
                pass
            else:
                logger.warn(
                    f'User {user_id} tried to re-authenticate wearable {wearable}, but '
                    f'current terra_user_id ({user_wearable.terra_user_id}) does not match '
                    f'old ({old_terra_user_id}) or new ({new_terra_user_id}). Ignoring.')
        else:
            user_wearable.terra_user_id = new_terra_user_id
            # Just in case
            user_wearable.registration_complete = True
            db.session.commit()
            logger.info(f'User {user_id} re-authenticated wearable {wearable}.')

    def access_revoked_response(self, response: terra.api.api_responses.TerraApiResponse):
        """ Handle access_revoked and connection_error webhook responses.

        This method is called when the user revokes access through the
        wearable provider. ``access_revoked`` response is given when
        Terra is informed of user revoking access. ``connection_error``
        happens when Terra is NOT informed, but fetching data fails.
        """
        terra_user_id = response.user.user_id
        wearable = response.user.provider

        user_wearable = (db.session.execute(
            select(WearablesV2)
            .filter_by(terra_user_id=terra_user_id))
            .one_or_none())

        if not user_wearable:
            logger.error(
                f'A user tried to revoke access for wearable {wearable}, '
                f'but Terra ID {terra_user_id} was not found in the DB.')
            return

        if response.dtype == 'connection_error':
            # Ask Terra to delete user.
            terra_user = self.from_user_id(terra_user_id)
            resp = self.deauthenticate_user(terra_user)
            self.status(resp)


        # TODO: delete data

        user_id = user_wearable.user_id
        user_wearable.delete()
        db.session.commit()

        logger.audit(
            f'User {user_id} revoked access to wearable {wearable}. Info and data deleted.')


@ns_v2.route('')
class WearablesV2Endpoint(BaseResource):
    @token_auth.login_required
    @responds(status_code=200, api=ns_v2)
    @lru_cache_with_ttl(maxsize=1, ttl=86400)
    def get(self):
        """ Get a list of all supported wearable devices. """
        tc = TerraClient()
        response = tc.list_providers()
        tc.status(response)
        return response.json


@ns_v2.route('/<uuid:uid>')
class WearablesV2UserEndpoint(BaseResource):
    @token_auth.login_required
    @responds(status_code=200, api=ns_v2)
    def get(self, uid):
        """ Get a list of wearable devices registered to this user. """
        user_id = self.check_user(uid, user_type='client').user_id

        wearables = (db.session.execute(
            select(
                WearablesV2.wearable)
            .filter_by(
                user_id=user_id))
            .scalars()
            .all())

        return {'wearables': wearables}


@ns_v2.route('/<uuid:uid>/<wearable>')
class WearablesV2DataEndpoint(BaseResource):
    @token_auth.login_required
    # @responds(schema=WearablesV2DataSchema, status_code=200, api=ns_v2)
    def get(self, uid, wearable):
        """ Get data for this combination of user and wearable device. """
        # return data for this user for this wearable
        pass

    @token_auth.login_required
    # @accepts(schema=WearablesV2RegisterSchema, status_code=201, api=ns_v2)
    def post(self, uid, wearable):
        """ Register a new wearable device for this user. """
        user_id = self.check_user(uid, user_type='client').user_id

        tc = TerraClient()
        response = tc.generate_authentication_url(
            resource=wearable,
            auth_success_redirect_url=request.parsed_object['auth_success_redirect_url'],
            auth_failure_redirect_url=request.parsed_object['auth_failure_redirect_url'],
            reference_id=uid)

        tc.status(response)

        user_wearable = WearablesV2(
            user_id=user_id,
            wearable=wearable,
            terra_user_id=response.json['user_id'])
        db.session.add(user_wearable)
        db.session.commit()

        return {'url': response.json['auth_url']}

    @token_auth.login_required
    @responds(status_code=204, api=ns)
    def delete(self, uid, wearable):
        """ Revoke access for this wearable device. """
        user_id = self.check_user(uid, user_type='client').user_id

        user_wearable = (db.session.execute(
            select(WearablesV2)
            .filter_by(user_id=user_id, wearable=wearable))
            .one_or_none())

        # Don't error on non-existant users, delete is idempotent
        if not user_wearable:
            return

        tc = TerraClient()
        terra_user = tc.from_user_id(user_wearable.terra_user_id)
        response = tc.deauthenticate_user(terra_user)
        tc.status(response)

        # TODO: delete data

        user_wearable.delete()
        db.session.commit()


@ns_v2.route('/terra')
class WearablesV2TerraWebHookEndpoint(BaseResource):
    @accepts(api=ns_v2)
    def post(self):
        """ Webhook for incoming notifications from Terra. """
        tc = TerraClient()
        response = tc.handle_flask_webhook(request)

        if response.dtype == 'auth':
            # Completion of new wearable registration for user,
            # initialized by POST /v2/wearables/<uid>/<wearable>
            tc.auth_response(response)
        elif response.dtype == 'user_reauth':
            # User authenticates again, new terra_user_id
            tc.reauth_response(response)
        elif response.dtype in ('access_revoked', 'connection_error'):
            # User revoked access through wearable provider
            # and provider informed Terra.
            tc.access_revoked_response(response)
        elif response.dtype == 'deauth':
            # User revoked access through our API at DELETE /v2/wearables/<uid>/<wearable>,
            # or we did so in response to connection_error.
            # In either case, there is nothing to do here.
            pass
        elif response.dtype == 'google_no_datasource':
            # uh, ok
            pass
        elif response.dtype == 'request_processing':
            # TODO: handle data
            pass
        elif OTHER TYPES OF DATA PROCESSING
        else:
            logger.error(
                f'Terra webhook response with unknown type {response.dtype}. '
                f'Full message: {response.json}')
