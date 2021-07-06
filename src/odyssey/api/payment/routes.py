import requests
import json

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.misc import check_client_existence
from odyssey.utils.errors import TooManyPaymentMethods, GenericNotFound, GenericThirdPartyError
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.payment.schemas import PaymentMethodsSchema

ns = api.namespace('payment', description='Endpoints for functions related to payments.')

@ns.route('/methods/<int:user_id>/')
class PaymentMethodsApi(Resource):
    
    @token_auth.login_required(user_type=('client',))
    @responds(schema=PaymentMethodsSchema(many=True), api=ns)
    def get(self, user_id):
        """get user payment methods"""
        check_client_existence(user_id)

        return PaymentMethods.query.filter_by(user_id=user_id).all()

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=PaymentMethodsSchema, api=ns)
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """add a new payment method"""
        check_client_existence(user_id)

        if len(PaymentMethods.query.filter_by(user_id=user_id).all()) >= 5:
            raise TooManyPaymentMethods

        request_data = {
            "Outlet": {
                "MerchantID": "InstaMed",
                "StoreID": "1",
                "TerminalID": "1"
            },
            "PaymentPlanType": "SaveOnFile",
            "PaymentMethod": "Card",
            "Card": {
                "EntryMode": "key",
                "CardNumber": request.json['token'],
                "Expiration": request.json['expiration']
            }
        }

        response = requests.post('https://connect.instamed.com/rest/payment/paymentplan',
                                headers={'Api-Key': current_app.config['INSTAMED_API_KEY'],
                                        'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                                        'Content-Type': 'application/json'},
                                json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            raise GenericThirdPartyError(response.status_code, response.text)

        #convert response data to json (python dict)
        response_data = json.loads(response.text)

        #if requesting to set this method to default and user already has a default 
        #payment method, remove default status from their previous default method
        old_default = PaymentMethods.query.filter_by(user_id=user_id, is_default=True).one_or_none()
        if request.json['is_default'] and old_default:
            old_default.update({'is_default': False})

        #then store the payment plan info from response in db
        payment_data = {
            'user_id': user_id,
            'payment_id': response_data['PaymentPlanID'],
            'number': response_data['CardResult']['LastFour'],
            'payment_type': response_data['CardResult']['Type'],
            'is_default': request.json['is_default']
        }

        payment = PaymentMethods(**payment_data)

        db.session.add(payment)
        db.session.commit()

        return payment

    @token_auth.login_required(user_type=('client',))
    @ns.doc(params={'idx': 'int',})
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=204)
    def delete(self, user_id):
        """remove an existing payment method"""
        idx = request.args.get('idx', type=int)

        payment = PaymentMethods.query.filter_by(idx=idx,user_id=user_id).one_or_none()
        
        if not payment:
            raise GenericNotFound(f'No payment method exists with idx {idx} and user id {user_id}.')

        db.session.delete(payment)
        db.session.commit()