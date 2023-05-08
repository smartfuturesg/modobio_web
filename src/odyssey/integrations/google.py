"""
This module contains the classes for handling interactions with google apis

Classes:
    GooglePlaystore - Class for handling interactions with the google playstore
        - we will validate subscriptions using the google playstore api
        - validation is a matter of sending a token to the api for verification

        
Sources:
    https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.subscriptionsv2/get


Notes:
    - use this API
        - GET https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{packageName}/purchases/subscriptionsv2/tokens/{token}

"""

from datetime import datetime
import os
import requests

from flask import current_app
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pytz import timezone

from odyssey.api.user.models import UserSubscriptions



class GooglePlaystore:

    def __init__(self):
        self.package_name = current_app.config.get('GOOGLE_PLAYSTORE_PACKAGE_NAME')
        self.access_token = self.get_access_token()


    def get_access_token():
        credentials = service_account.Credentials.from_service_account_file(
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )

        return credentials
    
    def process_subscription_response(response):
        """
        Processes the Google subscriptions API response and returns a dictionary with the
        subscription status, payment status, and cancellation status.

        Parameters
        ----------
        response : dict
            The JSON response from the Google subscriptions API.

        Returns
        -------
        dict
            A dictionary with the following keys:
                - 'is_active': A boolean indicating if the subscription is active or expired.
                - 'payment_status': A string representing the payment status ('pending', 'received', 'free_trial', or 'unknown').
                - 'cancel_reason': A string representing the cancellation reason ('user_canceled', 'payment_declined', 'unknown'), or None if not canceled.
        """
           
        result = {
            'is_active': False,
            'payment_status': None,
            'cancel_reason': None
        }

        if not response:
            return result

        # Check if the subscription is active
        current_time_utc = datetime.utcnow()
        current_time = int(current_time_utc.timestamp() * 1000)  # current UTC time in milliseconds
        expiry_time = int(response.get('expiryTimeMillis', 0))
        expiry_time = int(response.get('expiryTimeMillis', 0))
        auto_renewing = response.get('autoRenewing', False)

        if current_time < expiry_time and auto_renewing:
            # Subscription is active and auto-renewing
            result['is_active'] = True
        elif current_time < expiry_time:
            # Subscription is active but not auto-renewing
            result['is_active'] = True

        # Check the payment state
        payment_state = response.get('paymentState')
        if payment_state == 0:
            result['payment_status'] = 'pending'
        elif payment_state == 1:
            result['payment_status'] = 'received'
        elif payment_state == 2:
            result['payment_status'] = 'free_trial'
        else:
            result['payment_status'] = 'unknown'

        # Check the cancel reason if subscription is canceled
        cancel_reason = response.get('cancelReason')
        if cancel_reason is not None:
            if cancel_reason == 0:
                result['cancel_reason'] = 'user_canceled'
            elif cancel_reason == 1:
                result['cancel_reason'] = 'payment_declined'
            else:
                result['cancel_reason'] = 'unknown'

        return result
    
    def validate_subscription(self, subscription_id: str, purchase_token: str):
        """Use purchase token to validate subscription
        
        Parameters
        ----------
        subscription_id : str
            Unique identifier of the subscription type in the Google Play Console.
        purchase_token : str
            token from the client's purchase

        Returns
        -------
        dict
            response from google playstore api
        """
        
        # Create an API client
        api_client = build('androidpublisher', 'v3', credentials=self.access_token)
        
        try:
            # Call the API to validate the subscription
            result = api_client.purchases().subscriptions().get(
                packageName=self.package_name,
                subscriptionId=subscription_id,
                token=purchase_token
            ).execute()
        
        except Exception as e:
            print(f"Error validating subscription: {e}")
            return None
        



        return result
    
    def update_subscription(self, user_id: int, token: str = None):
        """Use purchase token to validate subscription and update subscription status on the modobio system.
        
        Parameters
        ----------
        user_id : int
            id of the user whose subscription is being update
        token : str
            token from the client's purchase

        Returns
        -------
        :class:`UserSubscriptions`
            updated subscription
        """
        if not token:
            subscription = UserSubscriptions.query.filter_by(user_id=user_id).first()
            token = subscription.playstore_token

        playstore_subscription = self.validate_subscription(token)

        
        
        # handle the payload
        if not playstore_subscription:
            return None
        

        
        
        # get subscription details
        subscription_details = playstore_subscription.get('subscriptionPurchase')
        subscription_id = subscription_details.get('subscriptionId')
        expiry_time = subscription_details.get('expiryTimeMillis')
        expiry_time = int(expiry_time) / 1000
        expiry_time = datetime.fromtimestamp(expiry_time)
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)
        
        # update subscription
        subscription = UserSubscriptions.query.filter_by(user_id=user_id, subscription_id=subscription_id).first()

        if subscription:
            subscription.expiry_time = expiry_time
            subscription.status = 'subscribed'

        return subscription