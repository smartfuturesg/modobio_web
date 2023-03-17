import logging

from datetime import datetime

import terra

from flask import current_app
from sqlalchemy import select
from terra.api.api_responses import TerraApiResponse, ConnectionErrorHookResponse
from werkzeug.exceptions import BadRequest

from odyssey import db, mongo
from odyssey.api.wearables.models import WearablesV2

logger = logging.getLogger(__name__)

WAY_BACK_WHEN = datetime(2010, 1, 1)


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
            elif response.json['type'] == 'large_request_sending':
                # Missing status
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
