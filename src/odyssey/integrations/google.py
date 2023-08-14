import json

import logging

from odyssey.api.lookup.models import LookupSubscriptions

logger = logging.getLogger(__name__)

from typing import Dict

from dateutil import parser
from flask import current_app
from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient
from werkzeug.exceptions import BadRequest


class PlayStore:
    def __init__(self):
        """
        Initializes the PlayStore class by creating service account credentials.

        """
        self.credentials = self.create_service_account_credentials(json.loads(current_app.config.get('GOOGLE_SERVICE_ACCOUNT_KEY')))

    def create_service_account_credentials(self, json_key: Dict[str, str]) -> service_account.Credentials:
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
            scopes=['https://www.googleapis.com/auth/androidpublisher']
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
        SUBSCRIPTION_STATE_CANCELLED - invalid
        SUBSCRIPTION_STATE_EXPIRED - invalid
        
        Args:
            subscription_state (str): The subscription state to validate.
        
        """

        valid_states = [
            'SUBSCRIPTION_STATE_ACTIVE',
            'SUBSCRIPTION_STATE_IN_GRACE_PERIOD'
        ]

        if subscription_state in valid_states:
            return True
        else:
            return False

    def verify_purchase(self, package_name: str, product_id: str, purchase_token: str) -> Dict:
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

        # get a list of all in app products
        # response = androidpublisher.inappproducts().list(packageName=package_name).execute() # old do not use
        # response = androidpublisher.monetization().subscriptions().list(packageName=package_name).execute()
        # print(response)
        # breakpoint()
        # get info on inapp product
        # response =  androidpublisher.inappproducts().get(packageName=package_name, sku=product_id).execute()
        # breakpoint()
        # log the arguments
        logger.info(f'\nVerifying purchase token: {purchase_token} for \nproduct: {product_id} in \npackage: {package_name}')
        try:
            response = androidpublisher.purchases().subscriptionsv2().get(
                packageName=package_name,
                # subscriptionId=product_id,
                token=purchase_token,
            ).execute()
            breakpoint()
        except googleapiclient.errors.HttpError as error:
            print(error)
            breakpoint()
            # print(error.resp.status)
            # print(error.resp.reason)
            # print(error.content)

        is_subscription_valid = self.validate_subscription_state(response.get('subscriptionState', ''))

        if not is_subscription_valid:
            return {'is_subscription_valid': False}

        start_timestamp = response['startTime']
        start_timestamp = parser.parse(start_timestamp)
        
        expiration_timestamp = response['lineItems']['expiryTime'] # timestamp in RFC3339 UTC "Zulu" format
        expiration_timestamp = parser.parse(expiration_timestamp)

        subscription_type_id = LookupSubscriptions.query.filter_by(product_id=response['lineItems']['productId']).first().id
        
        # If the request is successful, the response will contain details about the purchase
        return {'is_subscription_valid': True, 'start_timestamp': start_timestamp, 'expiration_timestamp': expiration_timestamp, 'subscription_type_id': subscription_type_id}

