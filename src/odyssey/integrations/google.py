import json

import logging

logger = logging.getLogger(__name__)

from typing import Dict

from flask import current_app
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import googleapiclient


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

    def verify_purchase(self, package_name: str, product_id: str, purchase_token: str) -> Dict:
        """
        Verifies a purchase token with the Google Play Developer API.

        Args:
            package_name (str): The package name of the app.
            subscription_id (str): The ID of the subscription.
            purchase_token (str): The purchase token to verify.

        Returns:
            dict: The response from the Google Play Developer API. If the token is valid, this will contain details about the purchase.
        """
        # Build the service
        androidpublisher = build('androidpublisher', 'v3', credentials=self.credentials)

        # get a list of all in app products
        # response = androidpublisher.inappproducts().list(packageName=package_name).execute()

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
        except googleapiclient.errors.HttpError as error:
            print(error)
            # print(error.resp.status)
            # print(error.resp.reason)
            # print(error.content)


        # If the request is successful, the response will contain details about the purchase
        # return response

