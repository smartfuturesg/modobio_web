import logging
from sqlalchemy import and_
logger = logging.getLogger(__name__)


from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.api.lookup.models import LookupOrganizations
from odyssey.api.payment.models import PaymentMethods, PaymentHistory, PaymentRefunds
from odyssey.api.payment.schemas import (
PaymentMethodsSchema,
PaymentHistorySchema,
PaymentRefundsSchema,
PaymentTestChargeVoidSchema,
TransactionHistorySchema)
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.user.models import User

ns = api.namespace('payment', description='Endpoints for functions related to payments.')

@ns.deprecated
@ns.route('/methods/<int:user_id>/')
class PaymentMethodsApi(BaseResource):
    # Multiple payment methods per user allowed
    __check_resource__ = False

    @token_auth.login_required(user_type=('client',))
    @responds(schema=PaymentMethodsSchema(many=True), api=ns)
    def get(self, user_id):
        """get active user payment methods"""
        self.check_user(user_id, user_type='client')

        return PaymentMethods.query.filter_by(user_id=user_id)

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=PaymentMethodsSchema, api=ns)
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """add a new payment method"""
        self.check_user(user_id, user_type='client')

        if len(PaymentMethods.query.filter(PaymentMethods.user_id == user_id,
                                           PaymentMethods.expiration.isnot(None)).all()) >= 5:
            raise BadRequest('Maximum number of payment methods reached.')

        #if requesting to set this method to default and user already has a default 
        #payment method, remove default status from their previous default method
        old_default = PaymentMethods.query.filter_by(user_id=user_id, is_default=True).one_or_none()
        if request.json['is_default'] and old_default:
            old_default.update({'is_default': False})

        #then store the payment plan info from response in db
        payment_data = {
            'user_id': user_id,
            'cardholder_name': request.json['cardholder_name'],
            'expiration': request.json['expiration'],
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
            
            #check if booking has been cancelled or completed. If so, remove it from the list.
            for booking in bookings:
                for status in booking.status_history:
                    if status.status in ('Cancelled', 'Canceled', 'Completed'):
                        bookings.remove(booking)
                        continue
                        
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
                    elif method.expiration == None:
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
                    e = BadRequest("This payment method cannot be deleted because it is involved with unpcoming unpaid bookings.")
                    e.data = {
                        'booking_ids': booking_ids,
                        'replacement_id': replacement_id
                    }
                    raise e
            
            #ensure card is not default and remove expiration date info
            payment.expiration = None
            payment.is_default = False
            db.session.commit()


@ns.deprecated
@ns.route('/history/<int:user_id>/')
class PaymentHistoryApi(BaseResource):

    @token_auth.login_required(user_type=('client', 'staff'), staff_role=('client_services',))
    @responds(schema=PaymentHistorySchema(many=True), api=ns, status_code=200)
    @ns.deprecated
    def get(self, user_id):
        """
        Returns a list of transactions for the given user_id.
        """
        self.check_user(user_id, user_type='client')

        return  PaymentHistory.query.filter_by(user_id=user_id).all()


@ns.deprecated
@ns.route('/transaction-history/<int:user_id>/')
class PaymentHistoryApi(BaseResource):

    @token_auth.login_required(user_type=('client', 'staff', 'staff-self'), staff_role=('client_services',))
    @responds(schema=TransactionHistorySchema, api=ns, status_code=200)
    def get(self, user_id):
        """
        Returns a list of transactions for the given user_id.
        """
        self.check_user(user_id, user_type='client')

        payload = {'items': []}

        for transaction in PaymentHistory.query.filter_by(user_id=user_id).all():
            transaction.__dict__.update({'transaction_date': transaction.created_at, 'currency' : 'USD', 'transaction_updated': transaction.updated_at, 'payment_method': transaction.payment_method})
            payload['items'].append(transaction.__dict__)

        return payload


@ns.deprecated
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
        raise BadRequest("This endpoint has been deprecated until a replacement for InstaMed has been implemented.")
        
        """self.check_user(user_id, user_type='client')

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

        return Instamed().refund_payment(original_transaction,
            request.parsed_obj.refund_amount,
            request.parsed_obj.refund_reason,
            reporter_id=token_auth.current_user()[0].user_id)"""