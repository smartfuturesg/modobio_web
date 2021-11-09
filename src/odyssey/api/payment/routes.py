import logging
logger = logging.getLogger(__name__)

import requests
import json

from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db
from odyssey.api import api
from odyssey.integrations.instamed import Instamed
from odyssey.utils.auth import token_auth
from odyssey.utils.misc import check_client_existence
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.telehealth import cancel_telehealth_appointment
from odyssey.api.lookup.models import LookupOrganizations
from odyssey.api.payment.models import PaymentMethods, PaymentStatus, PaymentHistory, PaymentRefunds
from odyssey.api.payment.schemas import (
PaymentMethodsSchema,
PaymentStatusSchema,
PaymentStatusOutputSchema,
PaymentHistorySchema,
PaymentRefundsSchema,
PaymentTestChargeVoidSchema,
PaymentTestRefundSchema)
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.user.models import User

ns = api.namespace('payment', description='Endpoints for functions related to payments.')

@ns.route('/methods/<int:user_id>/')
class PaymentMethodsApi(BaseResource):
    # Multiple payment methods per user allowed
    __check_resource__ = False

    @token_auth.login_required(user_type=('client',))
    @responds(schema=PaymentMethodsSchema(many=True), api=ns)
    def get(self, user_id):
        """get user payment methods"""
        self.check_user(user_id, user_type='client')

        return PaymentMethods.query.filter_by(user_id=user_id).all()

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=PaymentMethodsSchema, api=ns)
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """add a new payment method"""
        self.check_user(user_id, user_type='client')

        if len(PaymentMethods.query.filter_by(user_id=user_id).all()) >= 5:
            raise BadRequest('Maximum number of payment methods reached.')

        im = Instamed()

        response_data = im.add_payment_method(request.json['token'], request.json['expiration'], User.query.filter_by(user_id=user_id).one_or_none().modobio_id)

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
    @ns.doc(params={'idx': 'int id of the payment method to remove',
                    'replacement_id': 'int id of the payment method to replace the removed method with for future appointments. If the appointments should be canceled, use id 0.'})
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=204)
    def delete(self, user_id):
        """remove an existing payment method"""
        idx = request.args.get('idx', type=int)

        payment = PaymentMethods.query.filter_by(idx=idx, user_id=user_id).one_or_none()
        if payment:
            #check if payment is involved with future bookings
            bookings = TelehealthBookings.query.filter_by(payment_method_id=payment.idx, charged=False).all()
            if len(bookings) > 0:
                replacement_id = request.args.get('replacement_id', type=int)
                if replacement_id == 0:
                    #cancel appointments that are attached to the payment method being removed
                    for booking in bookings:
                        cancel_telehealth_appointment(booking)
                elif replacement_id:
                    #replace payment method on affected appointments with the new method
                    
                    #ensure replacement_id references an active payment method that belong to this user
                    method = PaymentMethods.query.filter_by(idx=replacement_id).one_or_none()
                    if not method:
                        raise BadRequest(f"No payment method exists the the id {replacement_id}.")
                    
                    if method.user_id != token_auth.current_user()[0].user_id:
                        raise BadRequest(f"The payment method with id {replacement_id} does not belong " \
                            "to the current user. Please use a valid payment method id that belongs to the " \
                            "current user.")
                    elif method.token == None:
                        #this method has been removed, it only exists to be displayed in history
                        raise BadRequest(f"The payment method with id {replacement_id} has been removed, " \
                            "it can no longer be charged.")
                    else:
                        #replace payment_method_id in the affected bookings
                        for booking in bookings:
                            booking.payment_method_id = replacement_id
                        db.session.flush()
                else:
                    #no replacement id was provided, raise error
                    booking_ids = []
                    for booking in bookings:
                        booking_ids += str(booking.idx)
                    booking_ids = ",".join(booking_ids)
                    raise BadRequest(f"The payment method with id {idx} is involed with the following booking " \
                        "ids: {booking_ids}. Please send another request with the replacement_id argument set to " \
                        "a valid payment id for the userif you would like to replace the payment methods on these " \
                        "booking with a new method. Alternatively, send another request with replacement_id argument "\
                        "set to 0 to cancel the affected appointments.")
            
            #remove token so card can't be charged anymore
            payment.payment_id = None
            #ensure card is not default and remove expiration date info
            payment.expiration = None
            payment.is_default = False
            db.session.commit()

@ns.route('/status/')
class PaymentStatusApi(BaseResource):
    @accepts(schema=PaymentStatusSchema, api=ns)
    @responds(schema=PaymentStatusSchema, api=ns, status_code=200)
    def post(self):
        self.check_user(request.parsed_obj.user_id, user_type='client')

        #retrieve token from header
        org_token = request.headers.get('Authorization')

        if not LookupOrganizations.query.filter_by(org_token=org_token, org_name='InstaMed').one_or_none():
            raise Unauthorized('Invalid organization token.')

        db.session.add(request.parsed_obj)
        db.session.commit()
        return request.parsed_obj

@ns.route('/status/<int:user_id>/')
class PaymentStatusGetApi(BaseResource):
    @token_auth.login_required(user_type=('client', 'staff',), staff_role=('client_services',))
    @responds(schema=PaymentStatusOutputSchema, api=ns, status_code=200)
    def get(self, user_id):
        self.check_user(user_id, user_type='client')

        return {'payment_statuses': PaymentStatus.query.filter_by(user_id=user_id).all()}

@ns.route('/history/<int:user_id>/')
class PaymentHistoryApi(BaseResource):
    @token_auth.login_required(user_type=('client', 'staff',), staff_role=('client_services',))
    @responds(schema=PaymentHistorySchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns a list of transactions for the given user_id.
        """
        self.check_user(user_id, user_type='client')

        return  PaymentHistory.query.filter_by(user_id=user_id).all()

@ns.route('/refunds/<int:user_id>/')
class PaymentRefundApi(BaseResource):
    # Multiple refunds allowed
    __check_resource__ = False

    @token_auth.login_required(user_type=('client', 'staff',), staff_role=('client_services',))
    @responds(schema=PaymentRefundsSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns all refunds that have been issued for the given user_id
        """
        self.check_user(user_id, user_type='client')

        return PaymentRefunds.query.filter_by(user_id=user_id).all()

    @token_auth.login_required(user_type=('staff',), staff_role=('client_services',))
    @accepts(schema=PaymentRefundsSchema, api=ns)
    @responds(schema=PaymentRefundsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """
        Issue a refund for a user. Multiple refunds may be issued for a single transaction, but the
        total amount refunded cannot exceed the amount of the original transaction.
        """
        
        self.check_user(user_id, user_type='client')

        payment_id = request.parsed_obj.payment_id

        #retrieve original transaction being refunded
        original_transaction = PaymentHistory.query.filter_by(idx=payment_id).one_or_none()
        if not original_transaction:
            raise BadRequest(f'Transaction {payment_id} not found.')

        #check if requested amount plus previous refunds of this transaction exceed the original amount
        total_refunded = 0.00
        for transaction in PaymentRefunds.query.filter_by(payment_id=payment_id).all():
            total_refunded += float(transaction.refund_amount)
    
        if (float(request.parsed_obj.refund_amount) + total_refunded) > float(original_transaction.transaction_amount):
            raise BadRequest(
                f'The requested refund amount combined with refunds already given '
                f'cannot exceed the amount of the original transaction. {total_refunded} '
                f'has already been refunded for the transaction with id {payment_id} and '
                f'the original transaction amount is {original_transaction.transaction_amount}.')

        return Instamed().refund_payment(original_transaction.transaction_id,
            request.parsed_obj.refund_amount,
            TelehealthBookings.query.filter_by(idx=original_transaction.booking_id).one_or_none(),
            request.parsed_obj.refund_reason)

# Development-only Namespace, sets up endpoints for testing payments.
ns_dev = Namespace(
    'payment',
    path='/payment/test',
    description='[DEV ONLY] Endpoints for testing payments.')

@ns_dev.route('/charge/')
class PaymentTestCharge(BaseResource):
    """
    [DEV ONLY] This endpoint is used for testing purposes only. It can be used by a system admin to test
    charging in the InstaMed system. 

    Note
    ---
    **This endpoint is only available in DEV environments.**

    """
    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',), dev_only=True)
    @accepts(schema=PaymentTestChargeVoidSchema, api=ns_dev)
    def post(self):
        booking = TelehealthBookings.query.filter_by(idx=request.parsed_obj['booking_id']).one_or_none()
        if not booking:
            raise BadRequest('No booking exists with booking id {booking_id}.'.format(**request.parsed_obj))
        if booking.charged:
            raise BadRequest('The booking with booking id {booking_id} has already been charged.'.format(**request.parsed_obj))

        return  Instamed().charge_user(booking)

@ns_dev.route('/void/')
class PaymentVoidRefund(BaseResource):
    """
    [DEV ONLY] This endpoint is used for testing purposes only. It can be used by a system admin to test
    voids in the InstaMed system.
    
    Note
    ---
    **This endpoint is only available in DEV environments.**

    """
    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',), dev_only=True)
    @accepts(schema=PaymentTestChargeVoidSchema, api=ns_dev)
    def post(self):
        #send InstaMed void request
        booking = TelehealthBookings.query.filter_by(idx=request.parsed_obj['booking_id']).one_or_none()
        if not booking:
            raise BadRequest('No booking exists with booking id {booking_id}.'.format(**request.parsed_obj))
        if not booking.charged:
            raise BadRequest('The booking with booking id {booking_id}'.format(**request.parsed_obj) + \
            'has not been charged yet,so it cannot be voided.')
        return Instamed().void_payment(booking, "Test void functionality")