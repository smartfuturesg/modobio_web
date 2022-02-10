import logging
logger = logging.getLogger(__name__)

import requests
from werkzeug.exceptions import BadRequest

from flask import current_app

from werkzeug.exceptions import BadRequest
from odyssey.api.payment.models import PaymentHistory, PaymentMethods, PaymentRefunds
from odyssey.api.user.models import User
from odyssey.api.staff.models import StaffCalendarEvents
from odyssey.utils.telehealth import update_booking_status_history

from odyssey import db

class Instamed:
    """ A class for performing common InstaMed API calls """

    def __init__(self):
        """ 
        Prepare the isntamed object
        """
        self.request_header = {'Api-Key': current_app.config.get('INSTAMED_API_KEY'),
                                        'Api-Secret': current_app.config.get('INSTAMED_API_SECRET'),
                                        'Content-Type': 'application/json'}
        self.url_base = "https://connect.instamed.com/rest"
        self.outlet = {
                "MerchantID": current_app.config.get('INSTAMED_API_KEY'),
                "StoreID": '0001',
                "TerminalID": '0002'
        }

    def add_payment_method(self, token, expiration, modobio_id):
        """
        Add a payment method for a user and save the reference token in our db.
        InstaMed URI: /payment/paymentplan


        Params
        ------
        token: (string)
            tokenized card information provided by an InstaMed FE component
        
        expiration: (string)
            card expiration date
        
        Returns
        -------
        dict of information regarding the newly saved payment method
        """

        request_data = {
            "Outlet": self.outlet,
            "PaymentPlanType": "SaveOnFile",
            "PaymentMethod": "Card",
            "Card": {
                "EntryMode": "key",
                "CardNumber": token,
                "Expiration": expiration
            },
            "Patient": {
                "AccountNumber": modobio_id
            }
        }

        response = requests.post(self.url_base + '/payment/paymentplan',
                                headers=self.request_header,
                                json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'Instamed returned the following error: {response.text}')

        return response.json()
    
    def refund_payment(self, transaction_id, amount, booking, reason, reporter_id=None):
        """
        Refund a payment.
        InstaMed URI: /payment/refund


        Params
        ------
        transaction_id: (string)
            InstaMed ID for the transaction to be refunded
        
        amount: (string)
            amount of money to be refunded
        
        booking: TelehealthBooking object
            object for the booking this transaction is associated with

        reason:
            reason for this refund

        reporter_id:
            id the the staff that approved this refund, None if system automated

        Returns
        -------
        dict of information regarding the refund
        """
        request_data = {
            "Outlet": self.outlet,
            "TransactionID": str(transaction_id),
            "Amount": str(amount),
            "Patient": {
                "AccountNumber": User.query.filter_by(user_id=booking.client_user_id).one_or_none().modobio_id
            }
        }

        response = requests.post(self.url_base + '/payment/refund-simple',
                        headers=self.request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            logger.error(f'Instamed returned the following error: {response.text} when' \
                f' refunding a transaction with id {transaction_id}.')
            raise BadRequest(f'Instamed returned the following error: {response.text}')
            

        refund_data = {
            'user_id': booking.client_user_id,
            'reporter_id': reporter_id,
            'payment_id': PaymentHistory.query.filter_by(transaction_id=transaction_id).one_or_none().idx,
            'refund_transaction_id': response.json()['TransactionID'],
            'refund_amount': amount,
            'refund_reason': reason
        }

        refund = PaymentRefunds(**refund_data)

        db.session.add(refund)
        db.session.commit()

        return refund_data

    def void_payment(self, booking, reason):
        """
        Void a payment before it has been processed. If the transfer of funds has already
        started, refund must be used instead.

        InstaMed URI: /payment/void

        Params
        ------
        booking: (TelehealthBookings object)
            the booking for which this payment is associated with
        
        Returns
        -------
        dict of information regarding the void
        """
        transaction = PaymentHistory.query.filter_by(booking_id=booking.idx).one_or_none()
        if not transaction.transaction_id:
            raise BadRequest(f'No transaction exists for the booking with booking id {booking.idx}.')

        request_data = {
            "Outlet": self.outlet,
            "TransactionID": str(transaction.transaction_id),
            "Patient": {
                "AccountNumber": User.query.filter_by(user_id=booking.client_user_id).one_or_none().modobio_id
            }
        }

        response = requests.post(self.url_base + '/payment/void',
                        headers=self.request_header,
                        json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            logger.error(f'Instamed returned the following error: {response.text} when' \
                f' voiding a transaction with id {transaction.transaction_id}.')
            raise BadRequest(f'Instamed returned the following error: {response.text}')

        #update transaction in PaymentHistory with void data
        transaction.voided = True
        transaction.void_reason = reason
        transaction.void_id = response.json()['TransactionID']
        db.session.commit()

        return response.json()

    def charge_user(self, booking):
        """
        Charge a user.
        InstaMed URI: /payment/sale


        Params
        ------
        booking: (TelehealthBookings object)
            the booking for which this payment is associated with
        
        Returns
        -------
        dict of information regarding the sale
        """
        request_data = {
            "Outlet": self.outlet,
            "PaymentMethod": "OnFile",
            "PaymentMethodID": str(PaymentMethods.query.filter_by(idx=booking.payment_method_id).one_or_none().payment_id),
            "Amount": str(booking.consult_rate),
            "Patient": {
                "AccountNumber": User.query.filter_by(user_id=booking.client_user_id).one_or_none().modobio_id
            }
        }

        response = requests.post(self.url_base + '/payment/sale',
                        headers=self.request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            #transaction was not successful, cancel booking
            cancel_telehealth_appointment(booking)
            return

        #convert response data to json (python dict)
        response_data = response.json()

        #check if card was declined or partially approved
        #(this is not an error as checked above since 200 is returned from InstaMed)
        if response_data['TransactionStatus'] == 'C':
            if response_data['IsPartiallyApproved']:
                #void the payment and cancel appointment
                request_data = {
                    "Outlet": self.outlet,
                    "TransactionID": str(response_data['TransactionID']),
                    "Patient": {
                        "AccountNumber": User.query.filter_by(user_id=booking.client_user_id).one_or_none().modobio_id
                    }
                }

                history = PaymentHistory(**{
                    'user_id': booking.client_user_id,
                    'payment_method_id': booking.payment_method_id,
                    'transaction_id': response_data['TransactionID'],
                    'transaction_amount': booking.consult_rate,
                    'booking_id': booking.idx
                })

                response = requests.post(self.url_base + '/payment/void',
                                headers=self.request_header,
                                json=request_data)
                
                #check if instamed api raised an error
                try:
                    response.raise_for_status()
                except:
                    logger.error(f'Instamed returned the following error: {response.text} when' \
                        ' voiding a partial transaction.')

                cancel_telehealth_appointment(booking)

                #add void data to history and commit
                history.voided = True
                history.void_reason = "Partial payment received"
                history.void_id = response.json()['TransactionID']
                db.session.add(history)
                db.session.commit()
                return "Partial payment received. Appointment has been canceled and partial payment has been voided", 400
            else:
                #transaction was successful, store in PaymentHistory
                history = PaymentHistory(**{
                    'user_id': booking.client_user_id,
                    'payment_method_id': booking.payment_method_id,
                    'transaction_id': response_data['TransactionID'],
                    'transaction_amount': booking.consult_rate,
                    'booking_id': booking.idx
                })
                db.session.add(history)
                booking.charged = True
                db.session.commit()
        else:
            #transaction was declined, cancel appointment
            cancel_telehealth_appointment(booking)
        return response_data

def cancel_telehealth_appointment(booking, refund=False, reason='Failed Payment'):
    """
    Used to cancel an appointment in the event a payment is unsuccessful
    and from bookings PUT to cancel a booking

    args:
    booking: a booking object for the telehealth appointment to be canceled
    refund: boolean denoting whether this booking should be refunded, should only happen when called
    due to practitioner cancellation or practitioner no-show
    reason: reason for the cancellation, either (Practitioner Cancellation, Practitioner No-Show, or Failed Payment)
    reporter_id: user_id of the user that initiated the cancellation, null if system automated
    reporter_role: role of the user that initiated the cancellation(staff or client), System if system automated
    """

    # update booking status to canceled
    booking.status = 'Canceled'

    # delete booking from Practitioner's calendar
    staff_event = StaffCalendarEvents.query.filter_by(location='Telehealth_{}'.format(booking.idx)).one_or_none()
    if staff_event:
        db.session.delete(staff_event)

    # add new status to status history table
    #update_booking_status_history('Canceled', booking.idx, reporter_id, reporter_role)

    if refund:
        #check if booking has been charged yet, if not do nothing
        history = PaymentHistory.query.filter_by(booking_id=booking.idx).one_or_none()
        if history:
            #first attempt to void, if that fails payment was likely more than 24 hours ago
            #in which case we should refund instead of void
            im = Instamed()
            try:
                im.void_payment(booking, reason)
            except:
                im.refund_payment(history.transaction_id, booking.consult_rate, booking, reason)

    #TODO: Create notification/send email(?) to user that their appointment 

    db.session.commit()
    return