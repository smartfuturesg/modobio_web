from datetime import datetime, timedelta

from flask import current_app, request, url_for
from flask_accepts import accepts, responds
from flask_restx import Resource
from requests_oauthlib import OAuth2Session

from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import (
    ClientDeniedAccess,
    ContentNotFound,
    IllegalSetting,
    MethodNotAllowed,
    UnknownError
)
from odyssey.models.wearables import Wearables, WearablesOura
from odyssey.utils.schemas import WearablesSchema, WearablesOuraSchema
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
        check_client_existence(clientid)

        wearables = Wearables.query.filter_by(clientid=clientid).one_or_none()
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
        query = Wearables.query.filter_by(clientid=clientid)
        wearables = query.one_or_none()

        if wearables:
            raise MethodNotAllowed

        # Prevent user from changing ID
        if request.json.get('clientid'):
            raise IllegalSetting(param='clientid')

        wearables = Wearables(clientid=clientid, **request.json)
        db.session.add(wearables)
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

        # Prevent user from changing ID
        if request.json.get('clientid'):
            raise IllegalSetting(param='clientid')

        query.update(request.json)
        db.session.commit()


@ns.route('/oura/<int:clientid>/')
@ns.doc(params={'clientid': 'Client ID number'})
class WearablesOuraAuthorizationEndpoint(Resource):
    @token_auth.login_required
    @responds({'name': 'url', 'type': str}, status_code=200, api=ns)
    def get(self, clientid):
        """ Oura Ring access grant URL for client ``clientid`` in reponse to a GET request.

        Parameters
        ----------
        clientid : int
            Client ID number.

        Returns
        -------
        str
            The URL where the client needs to go to grant access to Modo Bio.
        """
        # FLASK_DEV=local has no access to AWS
        if not current_app.config['OURA_CLIENT_ID']:
            return {'url': ''}

        check_client_existence(clientid)

        wearables = Wearables.query.filter_by(clientid=clientid).one_or_none()
        if not wearables or not wearables.has_oura:
            raise ContentNotFound

        client_id = current_app.config['OURA_CLIENT_ID']
        base_url = current_app.config['OURA_AUTH_URL']

        # flask_restx mangles endpoint name for '/oura/callback'
        redirect_url = url_for('api.wearables_wearables_oura_callback_endpoint', _external=True)

        oauth_session = OAuth2Session(client_id, redirect_uri=redirect_url)
        auth_url, state = oauth_session.authorization_url(base_url)

        # Store state in database
        oura = WearablesOura.query.filter_by(clientid=clientid).one_or_none()
        if not oura:
            oura = WearablesOura(clientid=clientid, oauth_state=state)
            db.session.add(oura)
        else:
            oura.oauth_state = state
        db.session.commit()

        return {'url': auth_url}


@ns.route('/oura/callback/')
class WearablesOuraCallbackEndpoint(Resource):
    @responds(status_code=200, api=ns)
    def get(self):
        """ Oura Ring callback URL """
        if not current_app.config['OURA_CLIENT_ID']:
            return 'Nothing done'

        oauth_state = request.args.get('state')
        error_code = request.args.get('error')
        oauth_grant_code = request.args.get('code')

        if error_code:
            if error_code == 'access_denied':
                raise ClientDeniedAccess
            else:
                raise UnknownError(message='Unknown error: {error_code}')

        if not oauth_grant_code:
            raise UnknownError(message='OAuth token empty, but no error message.')

        if not oauth_state:
            raise IllegalSetting(message='OAuth state changed between requests.')

        # Oura does not send any extra parameters, so the only parameter we can
        # use to identify client is state.
        oura = WearablesOura.query.filter_by(oauth_state=oauth_state).one_or_none()
        if not oura:
            raise IllegalSetting(message='OAuth state changed between requests.')

        # Store grant code so client does not have to repeat the
        # process in case the next part fails.
        oura.grant_token = oauth_grant_code
        db.session.commit()

        # Exchange access grant code for access token
        oura_id = current_app.config['OURA_CLIENT_ID']
        oura_secret = current_app.config['OURA_CLIENT_SECRET']
        token_url = current_app.config['OURA_TOKEN_URL']
        redirect_url = url_for('api.wearables_wearables_oura_callback_endpoint', _external=True)

        oauth_session = OAuth2Session(
            oura_id,
            state=oauth_state,
            redirect_uri=redirect_url
        )
        oauth_reply = oauth_session.fetch_token(
            token_url,
            code=oauth_grant_code,
            include_client_id=True,
            client_secret=oura_secret
        )

        if not oauth_session.authorized:
            raise UnknownError('Exchange of grant code into access token failed.')

        oura.access_token = oauth_reply['access_token']
        oura.refresh_token = oauth_reply['refresh_token']
        oura.token_expires = datetime.utcnow() + timedelta(seconds=oauth_reply['expires_in'])
        db.session.commit()

        # Everything was successful
        wearables = Wearables.query.filter_by(clientid=oura.clientid).first()
        wearables.registered_oura = True
        oura.grant_token = None
        oura.oauth_state = None
        db.session.commit()

        return 'OK'
