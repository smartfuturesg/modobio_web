import secrets

from datetime import datetime, timedelta

from flask import current_app, request, url_for
from flask_accepts import accepts, responds
from flask_restx import Resource
from requests_oauthlib import OAuth2Session
from sqlalchemy.sql import text

from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import (
    ClientDeniedAccess,
    ContentNotFound,
    IllegalSetting,
    MethodNotAllowed,
    UnknownError,
    UserNotFound
)
from odyssey.models.wearables import (
    Wearables,
    WearablesOura,
    WearablesFreeStyle
)
from odyssey.utils.schemas import (
    WearablesSchema,
    WearablesFreeStyleSchema,
    WearablesFreeStyleActivateSchema
)
from odyssey.models.wearables import Wearables, WearablesOura
from odyssey.utils.schemas import WearablesSchema, WearablesOuraAuthSchema
from odyssey.utils.misc import check_client_existence

from odyssey import db

ns = api.namespace('wearables', description='Endpoints for registering wearable devices.')

@ns.route('/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class WearablesEndpoint(Resource):
    @token_auth.login_required
    @responds(schema=WearablesSchema, status_code=200, api=ns)
    def get(self, clientid):
        """ Wearable device information for client ``clientid`` in response to a GET request.

        This endpoint returns information on which wearables a client has. For
        each supported wearable device, two keys exist in the returned dictionary:
        ``has_<device_name>`` to indicate whether or not the client has this device,
        and ``registered_<device_name>`` to indicate whether or not the registration
        of the wearable device with Modo Bio was completed successfully.

        Parameters
        ----------
        clientid : int
            Client ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        wearables = (
            Wearables.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        if not wearables:
            raise ContentNotFound

        return wearables

    @token_auth.login_required
    @accepts(schema=WearablesSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, clientid):
        """ Create new wearables information for client ``clientid`` in reponse to a POST request.

        Parameters
        ----------
        clientid : int
            Client ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        wearables = (
            Wearables.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        if wearables:
            raise MethodNotAllowed

        request.parsed_obj.clientid = clientid
        db.session.add(request.parsed_obj)
        db.session.commit()

    @token_auth.login_required
    @accepts(schema=WearablesSchema, api=ns)
    @responds(status_code=204, api=ns)
    def put(self, clientid):
        """ Update wearables information for client ``clientid`` in reponse to a PUT request.

        Parameters
        ----------
        clientid : int
            Client ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        query = Wearables.query.filter_by(clientid=clientid)
        wearables = query.one_or_none()

        if not wearables:
            raise ContentNotFound

        data = WearablesSchema().dump(request.parsed_obj)
        query.update(data)
        db.session.commit()


@ns.route('/oura/auth/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class WearablesOuraAuthEndpoint(Resource):
    @token_auth.login_required
    @responds(schema=WearablesOuraAuthSchema, status_code=200, api=ns)
    def get(self, clientid):
        """ Oura Ring OAuth2 parameters to initialize the access grant process.

        Parameters
        ----------
        clientid : int
            Client ID number.

        Returns
        -------
        dict
            JSON encoded dict containing:
            - oura_client_id
            - oauth_state
        """
        # FLASK_DEV=local has no access to AWS
        if not current_app.config['OURA_CLIENT_ID']:
            return

        wearables = (
            Wearables.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        # TODO: Disable this check until frontend has a way of setting has_oura
        #
        # wearables = Wearables.query.filter_by(clientid=clientid).one_or_none()
        # if not wearables or not wearables.has_oura:
        #     raise ContentNotFound

        oura_id = current_app.config['OURA_CLIENT_ID']
        state = secrets.token_urlsafe(24)

        # Store state in database
        oura = (
            WearablesOura.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        if not oura:
            oura = WearablesOura(clientid=clientid, oauth_state=state)
            db.session.add(oura)
        else:
            oura.oauth_state = state
        db.session.commit()

        return {'oura_client_id': oura_id, 'oauth_state': state}


@ns.route('/oura/callback/<int:clientid>/')
@ns.doc(params={
    'clientid': 'Client ID number',
    'state': 'OAuth2 state token',
    'code': 'OAuth2 access grant code',
    'redirect_uri': 'OAuth2 redirect URI'
})
class WearablesOuraCallbackEndpoint(Resource):
    @token_auth.login_required
    @responds(status_code=200, api=ns)
    def get(self, clientid):
        """ Oura Ring OAuth2 callback URL """
        if not current_app.config['OURA_CLIENT_ID']:
            raise UnknownError(message='This endpoint does not work in local mode.')

        check_client_existence(clientid)

        oura = WearablesOura.query.filter_by(clientid=clientid).one_or_none()
        if not oura:
            raise UnknownError(
                message=f'Clientid {clientid} not found in WearablesOura table. '
                         'Connect to /wearables/auth first.'
            )

        oauth_state = request.args.get('state')
        oauth_grant_code = request.args.get('code')
        redirect_uri = request.args.get('redirect_uri')

        if oauth_state != oura.oauth_state:
            raise UnknownError(message='OAuth state changed between requests.')

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
        # wearables = Wearables.query.filter_by(clientid=oura.clientid).first()
        # wearables.registered_oura = True

        db.session.commit()


@ns.route('/freestyle/activate/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class WearablesFreeStyleActivateEndpoint(Resource):
    @token_auth.login_required
    @responds(schema=WearablesFreeStyleActivateSchema, status_code=200, api=ns)
    def get(self, clientid):
        """ Returns CGM activation timestamp for client ``clientid`` in reponse to a GET request.

        Time data on the CGM sensor is stored as minutes since activation and as full
        timestamps in the database. Time data must be converted before it can be
        uploaded to the database, using the activation timestamp retrieved in this GET
        request.

        Parameters
        ----------
        clientid : int
            Client ID number.

        Returns
        -------
        str
            JSON encoded, ISO 8601 formatted datetime string.
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        if not cgm:
            raise ContentNotFound

        return cgm

    @token_auth.login_required
    @accepts(schema=WearablesFreeStyleActivateSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, clientid):
        """ Set new activation timestamp for client ``clientid`` in response to POST request.

        When a new CGM is activated, the activation timestamp must be stored in the database.

        Parameters
        ----------
        clientid : int
            Client ID number.

        timestamp : str
            ISO 8601 formatted datetime string.
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        if not cgm:
            cgm = WearablesFreeStyle(clientid=clientid)
            db.session.add(cgm)

        cgm.activation_timestamp = request.parsed_obj.activation_timestamp
        db.session.commit()


@ns.route('/freestyle/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class WearablesFreeStyleEndpoint(Resource):
    @token_auth.login_required
    @responds(schema=WearablesFreeStyleSchema, status_code=200, api=ns)
    def get(self, clientid):
        """ Return FreeStyle CGM data for client ``clientid`` in reponse to a GET request.

        Parameters
        ----------
        clientid : int
            Client ID number.

        Returns
        -------
        str
            JSON encoded dictionary
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        if not cgm:
            raise ContentNotFound

        return cgm

    @token_auth.login_required
    @accepts(schema=WearablesFreeStyleSchema, api=ns)
    @responds(status_code=201, api=ns)
    def put(self, clientid):
        """ Add data to current block for client ``clientid`` in reponse to a PUT request.

        Parameters
        ----------
        clientid : int
            Client ID number.
        """
        cgm = (
            WearablesFreeStyle.query
            .filter_by(clientid=clientid)
            .one_or_none()
        )

        if not cgm:
            msg =  f'FreeStyle Libre for client {clientid} has not yet been activated. '
            msg += f'Please send a POST request to /wearables/freestyle/activate/ first.'
            raise UnknownError(message=msg)

        if cgm.activation_timestamp != request.parsed_obj.activation_timestamp:
            msg =  f'Activation timestamp {request.parsed_obj.activation_timestamp} does not '
            msg += f'match current activation timestamp {cgm.activation_timestamp}. '
            msg += f'Please send a GET request to /wearables/freestyle/activate/ first.'
            raise UnknownError(message=msg)

        # Use array concatenation here, don't use:
        #    cgm.glucose = cgm.glucose + request.parsed_obj.glucose
        # See ... confluence page
        stmt = text('''
            UPDATE "WearablesFreeStyle"
            SET glucose = glucose || cast(:gluc as double precision[]),
                timestamps = timestamps || cast(:tstamps as timestamp without time zone[])
            WHERE clientid = :cid;
        ''').bindparams(
            gluc=request.parsed_obj.glucose,
            tstamps=request.parsed_obj.timestamps,
            cid=clientid
        )
        db.session.execute(stmt)
        db.session.commit()
