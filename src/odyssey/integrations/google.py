import json
import logging

from odyssey.api.lookup.models import LookupSubscriptions

logger = logging.getLogger(__name__)

from typing import Dict

import googleapiclient
from dateutil import parser
from flask import current_app
from google.oauth2 import service_account
from googleapiclient.discovery import build
from werkzeug.exceptions import BadRequest


class PlayStore:
    def __init__(self):
        """
        Initializes the PlayStore class by creating service account credentials.

        """
        self.credentials = self.create_service_account_credentials(
            json.loads(current_app.config.get('GOOGLE_SERVICE_ACCOUNT_KEY'))
        )

    def create_service_account_credentials(
        self, json_key: Dict[str, str]
    ) -> service_account.Credentials:
        """
        Creates service account credentials using the given JSON key.

        Args:
            json_key (Dict[str, str]): The JSON key for the service account.

        Returns:
            service_account.Credentials: The service account credentials.
        """
        # Create credentials from the service account info
        credentials = service_account.Credentials.from_service_account_info(
            json_key,
            scopes=['https://www.googleapis.com/auth/androidpublisher'],
        )

        return credentials

    def validate_subscription_state(self, subscription_state: str) -> bool:
        """
        Responds with weather or not the subscription state is valid.
        If valid, the user is considered to be currently subscribed.

        State can be one of the following values and are considered internally as either valid or invalid:

        SUBSCRIPTION_STATE_UNSPECIFIED - not valid
        SUBSCRIPTION_STATE_PENDING - not valid
        SUBSCRIPTION_STATE_ACTIVE - valid
        SUBSCRIPTION_STATE_PAUSED - invalid
        SUBSCRIPTION_STATE_IN_GRACE_PERIOD - valid
        SUBSCRIPTION_STATE_ON_HOLD - invalid
        SUBSCRIPTION_STATE_CANCELLED - valid (subscription is cancelled but not yet expired)
        SUBSCRIPTION_STATE_EXPIRED - invalid

        Args:
            subscription_state (str): One of three states possible: acvtive, grace_period, or invalid.

        """

        valid_states = [
            'SUBSCRIPTION_STATE_ACTIVE',
        ]

        grace_period_states = [
            'SUBSCRIPTION_STATE_IN_GRACE_PERIOD',
            'SUBSCRIPTION_STATE_CANCELED',
        ]

        if subscription_state in valid_states:
            return 'active'
        elif subscription_state in grace_period_states:
            return 'grace_period'
        else:
            return 'invalid'

    def verify_purchase(self, purchase_token: str) -> Dict:
        """
        Verifies a purchase token with the Google Play Developer API.

        Args:
            package_name (str): The package name of the app.
            subscription_id (str): The ID of the subscription.
            purchase_token (str): The purchase token to verify.

        Returns:
            dict
        """
        # Build the service
        androidpublisher = build('androidpublisher', 'v3', credentials=self.credentials)

        try:
            response = (
                androidpublisher.purchases().subscriptionsv2().get(
                    packageName=current_app.config['GOOGLE_PACKAGE_NAME'],
                    token=purchase_token,
                ).execute()
            )
        except googleapiclient.errors.HttpError as error:
            logger.error(error)

        logger.info(f"Subscription state, is {response.get('subscriptionState', '')}")

        subscription_state = self.validate_subscription_state(response.get('subscriptionState', ''))

        if subscription_state == 'invalid':
            return {'subscription_state': subscription_state}

        start_timestamp = response['startTime']
        start_timestamp = parser.parse(start_timestamp).replace(tzinfo=None)

        expiration_timestamp = response['lineItems'][0]['expiryTime']
        expiration_timestamp = parser.parse(expiration_timestamp).replace(tzinfo=None)

        subscription_type_id = (
            LookupSubscriptions.query.filter_by(
                google_product_id=response['lineItems'][0]['productId']
            ).first().sub_id
        )

        # If the request is successful, the response will contain details about the purchase
        return {
            'subscription_state': subscription_state,
            'start_timestamp': start_timestamp,
            'expiration_timestamp': expiration_timestamp,
            'subscription_type_id': subscription_type_id,
        }
