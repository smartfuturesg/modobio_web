import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from flask import current_app
from itsdangerous import base64_decode
from pytz import utc
import jwt
import json
import requests
from time import mktime
from typing import Dict
import uuid
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.lookup.models import LookupSubscriptions
from odyssey.api.user.models import UserSubscriptions
from odyssey.api.user.schemas import UserSubscriptionsSchema



class AppStore:
    """ Class that handles interaction with the Apple Appstore API """

    def __init__(self):
        self.bundle_id = current_app.config.get('APPLE_APPSTORE_BUNDLE_ID')
        self.private_api_key = current_app.config.get('APPLE_APPSTORE_API_KEY').replace('\\\n', '\n') # additional '\' added when reading in from env var (\\ in DEV)
        self.private_api_key = self.private_api_key.replace('\\n', '\n') # additional '\' added when reading in from env var
        self.api_key_id = current_app.config.get('APPLE_APPSTORE_API_KEY_ID')

    def _generate_auth_jwt(self):
        """
        Create JWT for authenticating Apple appstore requests.
        ref:  https://developer.apple.com/documentation/appstoreserverapi/generating_tokens_for_api_requests?changes=latest_major
        
        """

        token= jwt.encode( {
                    'iss': current_app.config.get('APPLE_APPSTORE_ISSUER_ID'),
                    'iat': int(mktime((datetime.now()).timetuple())) , 
                    'exp': int(mktime((datetime.now()+timedelta(minutes=20)).timetuple())), 
                    'aud': 'appstoreconnect-v1',
                    'nonce': str(uuid.uuid4()),
                    'bid': self.bundle_id},
                    self.private_api_key, 
                    headers ={
                            'alg': 'ES256',
                            'kid':self.api_key_id,
                            'typ': 'JWT'
                        }, 
                    algorithm='ES256')

        return token

    def latest_transaction(self, original_transaction_id: str):
        """
        User the appstore API to bring up the client's most recent transaction.

        Parameters
        ----------
        original_transaction_id : str
            ID unique to each client that can be used to track all appstore purchases

        Returns
        -------
        tuple(dict, dict, int)
            A tuple containing transaction_info, renewal_info, and status.
        """

        # query Apple Storekit for subscription status and details, update if necessary
        access_token = self._generate_auth_jwt()
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(current_app.config['APPLE_APPSTORE_BASE_URL'] + '/inApps/v1/subscriptions/' + original_transaction_id,
                headers=headers )
            
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'Apple AppStore returned the following error: {response.text}')

        payload = response.json()

        # extract signed transaction info and status from response. Should always be present given a valid originalTransactionID from apple
        transaction_jws = payload.get('data')[0].get('lastTransactions')[0].get('signedTransactionInfo')
        renewal_jws = payload.get('data')[0].get('lastTransactions')[0].get('signedRenewalInfo')

        status = payload.get('data')[0].get('lastTransactions')[0].get('status')
        
        # decode JWS payload, check the subscription product
        transaction_info = base64_decode(transaction_jws.split('.')[1])

        renewal_info = base64_decode(renewal_jws.split('.')[1])

        return  json.loads(transaction_info), json.loads(renewal_info), status

    @staticmethod
    def update_user_subscription(current_subscription: UserSubscriptions, transaction_info: dict):
        """
        Update user subscription:
        -end current subscription
        -create new subscription entry from transaction info
        
        Parameters
        ----------
        current_subscription : UserSubscriptions
            An instance of :class:`UserSubscriptions`

        transaction_info : dict
            From the response the Apple API subscription status request

        Returns
        -------
        UserSubscriptions
            A new instance of :class:`UserSubscriptions`
        """
        # end current subscription
        end_date = datetime.fromtimestamp(transaction_info['purchaseDate']/1000, utc)
        current_subscription.end_date = end_date
        current_subscription.subscription_status = 'unsubscribed'

        new_subscription_data = {
            'subscription_status': 'subscribed',
            'subscription_type_id': LookupSubscriptions.query.filter_by(ios_product_id = transaction_info.get('productId')).one_or_none().sub_id,
            'is_staff': current_subscription.is_staff,
            'last_checked_date': datetime.utcnow().isoformat(),
            'apple_original_transaction_id': current_subscription.apple_original_transaction_id
        }
        new_subscription = UserSubscriptionsSchema().load(new_subscription_data)
        new_subscription.user_id = current_subscription.user_id
        db.session.add(new_subscription)

        return new_subscription
