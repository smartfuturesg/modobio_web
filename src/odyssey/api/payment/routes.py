from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.misc import check_client_existence
from odyssey.utils.errors import TooManyPaymentMethods, GenericNotFound
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.payment.schemas import PaymentMethodsSchema

from odyssey.api.defaults import INSTAMED_API_SECRET, INSTAMED_API_KEY

ns = api.namespace('payment', description='Endpoints for functions related to payments.')

@ns.route('/methods/<int:user_id>/')
class PaymentMethodsApi(Resource):
    
    @token_auth.login_required(user_type=('Client',))
    @responds(schema=PaymentMethodsSchema, api=ns)
    def get(self, user_id):
        """get user payment methods"""
        check_client_existence(user_id)

        return PaymentMethods.query.filter_by(user_id=user_id).all()

    @token_auth.login_required(user_type=('Client',))
    @accepts(schema=PaymentMethodsSchema, api=ns)
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """add a new payment method"""
        check_client_existence(user_id)

        if PaymentMethods.query.filter_by(user_id=user_id).all() >= 5:
            raise TooManyPaymentMethods

        #todo: call instamed api /rest/payment/paymentplan/
        request_data = {
            "Outlet": {
                "MerchantID": "ModoBio",
                "StoreID": "1",
                "TerminalID": "1"
            },
            "PaymentPlanType": "SaveOnFile",
            "InitialAmount": 0,,
            "PaymentMethod": "Card",
            "Card": {
                "EntryMode": "token",
                "Token": "token",
            }
        }

        response = requests.post('https://connect.instamed.com/rest/payment/paymentplan',
                                headers={'Api-Key': current_app.config['INSTAMED_API_KEY'],
                                         'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                                         'Content-Type': 'application/json'})


        #then store the paymentPlanId from response in db
        request.parsed_obj.number = response.CardResult.LastFour
        request.parsed_obj.payment_type = response.CardResult.Type
        
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj


@ns.route('/methods/<int:idx>/')
class PaymentMethodsDelete(Resource):
    @token_auth.login_required(user_type=('Client',))
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=204)
    def delete(self, user_id):
        """remove an existing payment method"""
        payment = PaymentMethods.query.filter_by(idx=idx).one_or_none()
        
        if not payment:
            raise GenericNotFound

        session.db.delete(payment)
        session.db.commit()