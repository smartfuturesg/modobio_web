import base64
import secrets
from datetime import datetime, timedelta

from flask import current_app, request
from flask_accepts import accepts, responds
from flask_restx import Resource
from requests_oauthlib import OAuth2Session
from sqlalchemy.sql import text

from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.errors import (
    ContentNotFound,
    MethodNotAllowed,
    UnknownError
)

from odyssey.api.wearables.models import (
    Wearables,
    WearablesOura,
    WearablesFitbit,
    WearablesFreeStyle,
)

from odyssey.api.wearables.schemas import (
    WearablesSchema,
    WearablesOuraAuthSchema,
    WearablesFitbitGetSchema,
    WearablesFitbitPostSchema,
    WearablesFreeStyleSchema,
    WearablesFreeStyleActivateSchema,
)

from odyssey.utils.misc import check_client_existence
from odyssey import db

ns = api.namespace('wearables', description='Endpoints for registering wearable devices.')


###########################################################
#
# All wearables
#
###########################################################

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesEndpoint(Resource):
    @token_auth.login_required
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
            .one_or_none()
        )

        if not wearables:
            raise ContentNotFound

        return wearables

    @token_auth.login_required
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
        wearables = (
            Wearables.query
            .filter_by(user_id=user_id)
            .one_or_none()
        )

        if wearables:
            raise MethodNotAllowed

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

    @token_auth.login_required
    @accepts(schema=WearablesSchema, api=ns)
    @responds(status_code=204, api=ns)
    def put(self, user_id):
        """ Update wearables information for client ``user_id`` in reponse to a PUT request.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        query = Wearables.query.filter_by(user_id=user_id)
        wearables = query.one_or_none()

        if not wearables:
            raise ContentNotFound

        data = WearablesSchema().dump(request.parsed_obj)
        query.update(data)
        db.session.commit()


###########################################################
#
# Oura Ring
#
###########################################################

@ns.route('/oura/auth/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesOuraAuthEndpoint(Resource):
    @token_auth.login_required
    @responds(schema=WearablesOuraAuthSchema, status_code=200, api=ns)
    def get(self, user_id):
        """ Oura Ring OAuth2 parameters to initialize the access grant process.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict containing:
            - oura_client_id
            - oauth_state
        """
        # FLASK_DEV=local has no access to AWS
        if not current_app.config['OURA_CLIENT_ID']:
            raise UnknownError(message='This endpoint does not work in local mode.')

        wearables = (
            Wearables.query
            .filter_by(user_id=user_id)
            .one_or_none()
        )

        # TODO: Disable this check until frontend has a way of setting has_oura
        #
        # wearables = Wearables.query.filter_by(user_id=user_id).one_or_none()
        # if not wearables or not wearables.has_oura:
        #     raise ContentNotFound

        oura_id = current_app.config['OURA_CLIENT_ID']
        state = secrets.token_urlsafe(24)

        # Store state in database
        oura = (
            WearablesOura.query
            .filter_by(user_id=user_id)
            .one_or_none()
        )

        if not oura:
            oura = WearablesOura(user_id=user_id, oauth_state=state)
            db.session.add(oura)
        else:
            oura.oauth_state = state
        db.session.commit()

        return {'oura_client_id': oura_id, 'oauth_state': state}


@ns.route('/oura/callback/<int:user_id>/')
@ns.doc(params={
    'user_id': 'User ID number',
    'state': 'OAuth2 state token',
    'code': 'OAuth2 access grant code',
    'redirect_uri': 'OAuth2 redirect URI',
    'scope': 'The accepted scope of information: email, personal, and/or daily'
})
class WearablesOuraCallbackEndpoint(Resource):
    @token_auth.login_required
    @responds(status_code=200, api=ns)
    def get(self, user_id):
        """ Oura Ring OAuth2 callback URL """
        if not current_app.config['OURA_CLIENT_ID']:
            raise UnknownError(message='This endpoint does not work in local mode.')

        check_client_existence(user_id)

        oura = WearablesOura.query.filter_by(user_id=user_id).one_or_none()
        if not oura:
            raise UnknownError(
                message=f'user_id {user_id} not found in WearablesOura table. '
                         'Connect to /wearables/oura/auth first.'
            )

        oauth_state = request.args.get('state')
        oauth_grant_code = request.args.get('code')
        redirect_uri = request.args.get('redirect_uri')
        scope = request.args.get('scope')

        if oauth_state != oura.oauth_state:
            raise UnknownError(message='OAuth state changed between requests.')

        if not scope or 'daily' not in scope:
            raise UnknownError(message='You must agree to share at least the sleep and activity data.')

        # Exchange access grant code for access token
        oura_id = current_app.config['OURA_CLIENT_ID']
        oura_secret = current_app.config['OURA_CLIENT_SECRET']
        token_url = current_app.config['OURA_TOKEN_URL']

        oauth_session = OAuth2Session(
            oura_id,
            state=oauth_state,
            redirect_uri=redirect_uri
        )
        try:
            oauth_reply = oauth_session.fetch_token(
                token_url,
                code=oauth_grant_code,
                include_client_id=True,
                client_secret=oura_secret
            )
        except Exception as e:
            raise UnknownError(message=f'Error while exchanging grant code for access token: {e}')

        # Everything was successful
        oura.access_token = oauth_reply['access_token']
        oura.refresh_token = oauth_reply['refresh_token']
        oura.token_expires = datetime.utcnow() + timedelta(seconds=oauth_reply['expires_in'])
        oura.oauth_state = None

        # TODO: disable this until frontend has a way of setting wearable devices.
        # wearables = Wearables.query.filter_by(user_id=oura.user_id).first()
        # wearables.registered_oura = True

        db.session.commit()


###########################################################
#
# Fitbit
#
###########################################################

@ns.route('/fitbit/auth/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesFitbitAuthEndpoint(Resource):
    @token_auth.login_required
    @responds(schema=WearablesFitbitGetSchema, status_code=200, api=ns)
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
            - scope
        """
        # FLASK_DEV=local has no access to AWS
        if not current_app.config['FITBIT_CLIENT_ID']:
            raise UnknownError(message='This endpoint does not work in local mode.')

        # TODO: Disable this check until frontend has a way of setting has_fitbit
        # wearables = (
        #     Wearables.query
        #     .filter_by(user_id=user_id)
        #     .one_or_none()
        # )
        #
        # wearables = Wearables.query.filter_by(user_id=user_id).one_or_none()
        # if not wearables or not wearables.has_fitbit:
        #     raise ContentNotFound

        state = secrets.token_urlsafe(24)

        # Store state in database
        fitbit = (
            WearablesFitbit.query
            .filter_by(user_id=user_id)
            .one_or_none()
        )

        if not fitbit:
            fitbit = WearablesFitbit(user_id=user_id, oauth_state=state)
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
            'state': state
        }

    @token_auth.login_required
    @accepts(schema=WearablesFitbitPostSchema, api=ns)
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
        """
        # FLASK_DEV=local has no access to AWS
        if not current_app.config['FITBIT_CLIENT_ID']:
            raise UnknownError(message='This endpoint does not work in local mode.')

        check_client_existence(user_id)

        fitbit = WearablesFitbit.query.filter_by(user_id=user_id).one_or_none()
        if not fitbit:
            raise UnknownError(
                message=f'user_id {user_id} not found in WearablesFitbit table. '
                         'Connect to GET /wearables/fitbit/auth first.'
            )

        if request.parsed_obj['state'] != fitbit.oauth_state:
            raise UnknownError(message='OAuth state changed between requests.')

        # Exchange access grant code for access token
        client_id = current_app.config['FITBIT_CLIENT_ID']
        client_secret = current_app.config['FITBIT_CLIENT_SECRET']
        token_url = current_app.config['FITBIT_TOKEN_URL']
        auth_str = base64.urlsafe_b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')

        oauth_session = OAuth2Session(
            client_id,
            state=request.parsed_obj['state'],
            redirect_uri=request.parsed_obj['redirect_uri']
        )
        try:
            oauth_reply = oauth_session.fetch_token(
                token_url,
                code=request.parsed_obj['code'],
                include_client_id=True,
                client_secret=client_secret,
                headers = {'Authorization': f'Basic {auth_str}'}
            )
        except Exception as e:
            raise UnknownError(message=f'Error while exchanging grant code for access token: {e}')

        # Fitbit sends errors in body with a 200 response.
        if not oauth_reply.get('success', True):
            msg = oauth_reply['errors'][0]['message']
            raise UnknownError(message=f'fitbit.com returned error: {msg}')

        # Not requiring location, profile, settings, or social
        minimal_scope = set(current_app.config['FITBIT_SCOPE'].split())
        scope = set(oauth_reply.get('scope', []))

        if scope.intersection(minimal_scope) != minimal_scope:
            msg = 'You must agree to share at least: {}.'.format(', '.join(minimal_scope))
            raise UnknownError(message=msg)

        # Everything was successful
        fitbit.access_token = oauth_reply['access_token']
        fitbit.refresh_token = oauth_reply['refresh_token']
        fitbit.token_expires = datetime.utcnow() + timedelta(seconds=oauth_reply['expires_in'])
        fitbit.oauth_state = None

        wearables = Wearables.query.filter_by(user_id=user_id).one_or_none()

        # TODO: this is a temporary solution until frontend has a way of creating entries in Wearables.
        if not wearables:
            wearables = Wearables(
                user_id=user_id,
                has_fitbit=True,
                registered_fitbit=True
            )
            db.session.add(wearables)
        else:
            wearables.has_fitbit = True
            wearables.registered_fitbit = True

        db.session.commit()

    @token_auth.login_required
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
            .one_or_none()
        )

        if fitbit:
            db.session.delete(fitbit)

        wearables = (
            Wearables.query
            .filter_by(user_id=user_id)
            .one_or_none()
        )

        if wearables:
            wearables.registered_fitbit = False

        db.session.commit()


###########################################################
#
# FreeStyle Libre CGM
#
###########################################################

@ns.route('/freestyle/activate/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesFreeStyleActivateEndpoint(Resource):
    @token_auth.login_required
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
            .one_or_none()
        )

        if not cgm:
            raise ContentNotFound

        return cgm

    @token_auth.login_required
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
            .one_or_none()
        )

        if not cgm:
            cgm = WearablesFreeStyle(user_id=user_id)
            db.session.add(cgm)

        cgm.activation_timestamp = request.parsed_obj.activation_timestamp
        db.session.commit()


@ns.route('/freestyle/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class WearablesFreeStyleEndpoint(Resource):
    @token_auth.login_required
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
            .one_or_none()
        )

        if not cgm:
            raise ContentNotFound

        return cgm

    @token_auth.login_required
    @accepts(schema=WearablesFreeStyleSchema, api=ns)
    @responds(status_code=201, api=ns)
    def put(self, user_id):
        """ Add CGM data for client ``user_id`` in reponse to a PUT request.

        Parameters
        ----------
        user_id : int
            User ID number.
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(user_id=user_id)
            .one_or_none()
        )

        if not cgm:
            msg =  f'FreeStyle Libre for client {user_id} has not yet been activated. '
            msg += f'Send a POST request to /wearables/freestyle/activate/ first.'
            raise UnknownError(message=msg)

        if cgm.activation_timestamp != request.parsed_obj.activation_timestamp:
            msg =  f'Activation timestamp {request.parsed_obj.activation_timestamp} does not '
            msg += f'match current activation timestamp {cgm.activation_timestamp}. '
            msg += f'Send a GET request to /wearables/freestyle/activate/ first.'
            raise UnknownError(message=msg)

        tstamps = request.parsed_obj.timestamps
        glucose = request.parsed_obj.glucose

        if len(tstamps) != len(glucose):
            raise UnknownError(message='Data arrays not equal length.')

        if not tstamps:
            return

        if len(tstamps) != len(set(tstamps)):
            raise UnknownError(message='Duplicate timestamps in data.')

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
            cid=user_id
        )
        db.session.execute(stmt)
        db.session.commit()
