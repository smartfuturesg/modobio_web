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
from flask import current_app
from pytz import timezone
import requests

from odyssey.api.user.models import UserSubscriptions



class GooglePlaystore:

    def __init__(self):
        self.package_name = current_app.config.get('GOOGLE_PLAYSTORE_PACKAGE_NAME')
        self.api_key = current_app.config.get('GOOGLE_PLAYSTORE_API_KEY')
    
    def validate_subscription(self, token: str):
        """Use purchase token to validate subscription
        
        Parameters
        ----------
        token : str
            token from the client's purchase

        Returns
        -------
        dict
            response from google playstore api
        """
        
        url = f'https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{self.package_name}/purchases/subscriptions/tokens/{token}'
        params = {'key': self.api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
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