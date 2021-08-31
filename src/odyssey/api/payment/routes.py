import requests
import json

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import INSTAMED_OUTLET
from odyssey.utils.misc import check_client_existence
from odyssey.utils.errors import TooManyPaymentMethods, GenericNotFound, GenericThirdPartyError, UnauthorizedUser, MethodNotAllowed
from odyssey.utils.base.resources import BaseResource
from odyssey.api.lookup.models import LookupOrganizations
from odyssey.api.payment.models import PaymentMethods, PaymentStatus, PaymentHistory, PaymentRefunds
from odyssey.api.payment.schemas import PaymentMethodsSchema, PaymentStatusSchema, PaymentStatusOutputSchema, PaymentHistorySchema, PaymentRefundsSchema

ns = api.namespace('payment', description='Endpoints for functions related to payments.')

@ns.route('/methods/<int:user_id>/')
class PaymentMethodsApi(BaseResource):
    
    @token_auth.login_required(user_type=('client',))
    @responds(schema=PaymentMethodsSchema(many=True), api=ns)
    def get(self, user_id):
        """get user payment methods"""
        super().check_user(user_id, user_type='client')

        return PaymentMethods.query.filter_by(user_id=user_id).all()

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=PaymentMethodsSchema, api=ns)
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """add a new payment method"""
        super().check_user(user_id, user_type='client')

        if len(PaymentMethods.query.filter_by(user_id=user_id).all()) >= 5:
            raise TooManyPaymentMethods

        request_data = {
            "Outlet": INSTAMED_OUTLET,
            "PaymentPlanType": "SaveOnFile",
            "PaymentMethod": "Card",
            "Card": {
                "EntryMode": "key",
                "CardNumber": request.json['token'],
                "Expiration": request.json['expiration']
            }
        }

        request_headers = {'Api-Key': current_app.config['INSTAMED_API_KEY'],
                                        'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                                        'Content-Type': 'application/json'}

        response = requests.post('https://connect.instamed.com/rest/payment/paymentplan',
                                headers=request_headers,
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
            'expiration': request.json['expiration'],
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

@ns.route('/status/')
class PaymentStatusApi(BaseResource):
    @accepts(schema=PaymentStatusSchema, api=ns)
    @responds(schema=PaymentStatusSchema, api=ns, status_code=200)
    def post(self):
        super().check_user(request.parsed_obj.user_id, user_type='client')

        #retrieve token from header
        org_token = request.headers.get('Authorization')

        if not LookupOrganizations.query.filter_by(org_token=org_token, org_name='InstaMed').one_or_none():
            raise UnauthorizedUser(message='Invalid organization token.')

        db.session.add(request.parsed_obj)
        db.session.commit()
        return request.parsed_obj

@ns.route('/status/<int:user_id>/')
class PaymentStatusGetApi(BaseResource):
    @token_auth.login_required(user_type=('client', 'staff',), staff_role=('client_services',))
    @responds(schema=PaymentStatusOutputSchema, api=ns, status_code=200)
    def get(self, user_id):
        super().check_user(user_id, user_type='client')

        return {'payment_statuses': PaymentStatus.query.filter_by(user_id=user_id).all()}

@ns.route('/history/<int:user_id>/')
class PaymentHistoryApi(BaseResource):
    @token_auth.login_required(user_type=('client', 'staff',), staff_role=('client_services',))
    @responds(schema=PaymentHistorySchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns a list of transactions for the given user_id.
        """
        super().check_user(user_id, user_type='client')

        return  PaymentHistory.query.filter_by(user_id=user_id).all()

@ns.route('/refunds/<int:user_id>/')
class PaymentRefundApi(BaseResource):

    @token_auth.login_required(user_type=('client', 'staff',), staff_role=('client_services',))
    @responds(schema=PaymentRefundsSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns all refunds that have been issued for the given user_id
        """
        super().check_user(user_id, user_type='client')

        return PaymentRefunds.query.filter_by(user_id=user_id).all()

    @token_auth.login_required(user_type=('staff',), staff_role=('client_services',))
    @accepts(schema=PaymentRefundsSchema, api=ns)
    @responds(schema=PaymentRefundsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Issue a refund for a user. Multiple refunds may be issued for a single transaction, but the
        total amount refunded cannot exceed the amount of the original transaction.
        """
        
        super().check_user(user_id, user_type='client')

        payment_id = request.parsed_obj.payment_id

        #retrieve original transaction being refunded
        original_traction = PaymentHistory.query.filter_by(idx=payment_id).one_or_none()
        if not original_traction:
            raise GenericNotFound(f'No transaction with transaction_id {payment_id} exists.')

        #check if requested amount plus previous refunds of this transaction exceed the original amount
        total_refunded = 0.00
        for transaction in PaymentRefunds.query.filter_by(payment_id=payment_id).all():
            total_refunded += float(transaction.refund_amount)

        if float(request.parsed_obj.refund_amount) + total_refunded >= float(original_traction.transaction_amount):
            raise MethodNotAllowed(message='The requested refund amount combined with refunds already given' + \
                                            f' cannot exceed the amount of the original transaction. {total_refunded}' + \
                                            f'has already been refunded for the transaction id {payment_id}.')

        #call instamed api
        request_data = {
            "Outlet": INSTAMED_OUTLET,
            "TransactionID": original_traction.transaction_id,
            "Amount": request.parsed_obj.refund_amount
        }

        request_headers = {'Api-Key': current_app.config['INSTAMED_API_KEY'],
                                'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                                'Content-Type': 'application/json'}

        response = requests.post('https://connect.instamed.com/rest/payment/refund-simple',
                        headers=request_headers,
                        json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            raise GenericThirdPartyError(response.status_code, response.text)

        request.parsed_obj.user_id = user_id
        request.parsed_obj.reporter_id = token_auth.current_user()[0].user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj