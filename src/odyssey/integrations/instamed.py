from datetime import datetime
import logging
from odyssey.api.lookup.models import LookupRoles

from odyssey.api.telehealth.models import TelehealthBookings

from odyssey.api.lookup.models import LookupBookingTimeIncrements
logger = logging.getLogger(__name__)

import requests
from werkzeug.exceptions import BadRequest

from flask import current_app

from werkzeug.exceptions import BadRequest
from odyssey.api.payment.models import PaymentHistory, PaymentMethods, PaymentRefunds
from odyssey.api.user.models import User
from odyssey.api.staff.models import StaffCalendarEvents
from odyssey.utils.misc import create_notification

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
                "MerchantID": current_app.config.get('INSTAMED_MERCHANT_ID').replace('/',''),
                "StoreID": '0001',
                "TerminalID": '0002'
        }

    def add_payment_method(self, token, expiration, modobio_id):
        """
        Add a payment method for a user and save the reference token in our db.
        InstaMed URI: /payment/paymentplan


        Parameters
        ----------
        token : str
            tokenized card information provided by an InstaMed FE component

        expiration : str
            card expiration date

        Returns
        -------
        dict
            information regarding the newly saved payment method
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
        
        logger.info("Sending Instamed payment plan request")

        response = requests.post(self.url_base + '/payment/paymentplan',
                                headers=self.request_header,
                                json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            logger.error(f'Instamed returned the following error: {response.text} when' \
                f' adding a payment method.')
            raise BadRequest(f'Instamed returned the following error: {response.text}')

        return response.json()
    
    def refund_payment(self, payment: PaymentHistory, amount: str, reason: str, reporter_id: int=None):
        """
        Refund a payment.
        InstaMed URI: /payment/refund

        Parameters
        ----------
        transaction_id : str
            InstaMed ID for the transaction to be refunded

        amount : str
            amount of money to be refunded

        booking : :class:`TelehealthBooking` instance
            object for the booking this transaction is associated with

        reason : str
            reason for this refund

        reporter_id : int
            id the the staff that approved this refund, None if system automated

        Returns
        -------
        dict
            information regarding the refund
        """
        request_data = {
            "Outlet": self.outlet,
            "TransactionID": payment.transaction_id,
            "Amount": amount,
            "Patient": {
                "AccountNumber": User.query.filter_by(user_id=payment.user_id).one_or_none().modobio_id
            }
        }
        
        logger.info("Sending Instamed refund request")

        response = requests.post(self.url_base + '/payment/refund-simple',
                        headers=self.request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            logger.error(f'Instamed returned the following error: {response.text} when' \
                f' refunding a transaction with id {payment.transaction_id}.')
            raise BadRequest(f'Instamed returned the following error: {response.text}')
            

        refund_data = {
            'user_id': payment.user_id,
            'reporter_id': reporter_id,
            'payment_id': payment.idx,
            'refund_transaction_id': response.json()['TransactionID'],
            'refund_amount': amount,
            'refund_reason': reason
        }

        refund = PaymentRefunds(**refund_data)

        db.session.add(refund)
        db.session.commit()

        return refund_data

    def void_payment(self, payment_history_id: int, reason: str):
        """
        Void a payment before it has been processed. If the transfer of funds has already
        started, refund must be used instead.

        InstaMed URI: /payment/void

        Parameters
        ----------
        payment_history_id : int
            Payment id for the PaymentHistory entry.

        reason : str
            Reason for voiding the payment.

        Returns
        -------
        dict
            information regarding the void
        """
        transaction = PaymentHistory.query.filter_by(idx=payment_history_id).one_or_none()
        if not transaction:
            raise BadRequest(f'No transaction exists for the payment with id {payment_history_id}.')

        request_data = {
            "Outlet": self.outlet,
            "TransactionID": str(transaction.transaction_id),
            "Patient": {
                "AccountNumber": User.query.filter_by(user_id=transaction.user_id).one_or_none().modobio_id
            }
        }

        logger.info("Sending Instamed void request")

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

    def charge_user(self, user_id: int, amount: str, transaction_descriptor: str, payment_method_id: int = None, booking_id: int=None):
        """
        Charge a user.
        InstaMed URI: /payment/sale

        Parameters
        ----------
        user_id : int
            the booking for which this payment is associated with

        payment_method_id : int
            Refers to PaymentMethods.idx. Payment method selected by user for this transaction. 
            Defaults to their default payment method.

        amount : str
            tansaction ammount formatted for currency

        transaction_descriptor : str
            Standard format transaction description e.g. “Telehealth-MedicalDoctor-30mins”

        payment_method_id : int
            Refers to PaymentMethods.idx. Payment method to be used for the transaction. 
            If none specified, the default payment method for the user will be used

        Returns
        -------
        dict
            information regarding the instamed transaction
        """
        user = User.query.filter_by(user_id=user_id).one_or_none()
        payment_method =  PaymentMethods.query.filter_by(idx=payment_method_id).one_or_none() if payment_method_id \
                                        else PaymentMethods.query.filter_by(user_id=user_id, is_default=True).one_or_none()
        if not payment_method:
            raise BadRequest('user missing payment method')

        request_data = {
            "Outlet": self.outlet,
            "PaymentMethod": "OnFile",
            "PaymentMethodID": str(payment_method.payment_id),
            "Amount": amount,
            "Patient": {
                "AccountNumber": user.modobio_id
            }
        }
        
        logger.info("Sending Instamed sale request")

        response = requests.post(self.url_base + '/payment/sale',
                        headers=self.request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            # transaction was not successful, cancel booking
            #
            # TODO: Logging disabled for now 3.4.22, Alejandro will come back to this in NRV-2786
            # logger.error(f'Instamed returned the following error: {response.text} when' \
            #     f' attempting to charge booking with id {booking.idx}.')
            # cancel_telehealth_appointment(booking)
            # #create notification for failed payment
            # start_time = LookupBookingTimeIncrements.query \
            #     .filter_by(idx=booking.booking_window_id_start_time).one_or_none().start_time
            # payment_last_four = PaymentMethods.query \
            #     .filter_by(idx=booking.payment_method_id).one_or_none().number
            # create_notification(booking.client_user_id,
            #                     3, 
            #                     5, 
            #                     "Your Card Could Not Be Charged", 
            #                     f"Your telehealth appointment with {booking.practitioner.firstname} \
            #                     {booking.practitioner.lastname} at {start_time} on {booking.target_date}, \
            #                     unfortunately, had to be canceled as your payment method ending in \
            #                     {payment_last_four} could not be charged. Please revise your payment \
            #                     method or perhaps speak with your bank to resolve the issue")
            return {'is_successful': False}

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
                        "AccountNumber": user.modobio_id
                    }
                }

                history = PaymentHistory(**{
                    'user_id': user_id,
                    'payment_method_id': payment_method.idx,
                    'transaction_id': response_data['TransactionID'],
                    'transaction_amount': amount,
                    'transaction_descriptor': transaction_descriptor,
                    'authorization_number': response_data.get('AuthorizationNumber')
                })
                
                logger.info("Sending Instamed void request")

                response = requests.post(self.url_base + '/payment/void',
                                headers=self.request_header,
                                json=request_data)
                
                #check if instamed api raised an error
                try:
                    response.raise_for_status()
                except:
                    logger.error(f'Instamed returned the following error: {response.text} when' \
                        ' voiding a partial transaction.')

                # TODO: Notofication disabled for now 3.4.22, Alejandro will come back to this in NRV-2786
                # cancel_telehealth_appointment(booking)
                #
                # #create notification for failed payment
                # start_time = LookupBookingTimeIncrements.query \
                #     .filter_by(idx=booking.booking_window_id_start_time).one_or_none().start_time
                # payment_last_four = PaymentMethods.query \
                #     .filter_by(idx=booking.payment_method_id).one_or_none().number
                # create_notification(booking.client_user_id,
                #                     3, 
                #                     5, 
                #                     "Your Card Could Not Be Charged", 
                #                     f"Your telehealth appointment with {booking.practitioner.firstname} \
                #                     {booking.practitioner.lastname} at {start_time} on {booking.target_date}, \
                #                     unfortunately, had to be canceled as your payment method ending in \
                #                     {payment_last_four} could not be charged. Please revise your payment \
                #                     method or perhaps speak with your bank to resolve the issue")
            
                #add void data to history and commit
                history.voided = True
                history.void_reason = "Partial payment received"
                history.void_id = response.json()['TransactionID']
                db.session.add(history)
                db.session.flush()

                response_data['payment_history_id'] = history.idx
                response_data['is_successful'] = True
                response_data['is_partially_approved'] = True
            else:
                #transaction was successful, store in PaymentHistory
                history = PaymentHistory(**{
                    'user_id': user_id,
                    'payment_method_id': payment_method.idx,
                    'transaction_id': response_data['TransactionID'],
                    'transaction_amount': amount,
                    'transaction_descriptor': transaction_descriptor,
                    'authorization_number': response_data.get('AuthorizationNumber')
                })
                db.session.add(history)
                db.session.flush()
                
                response_data['payment_history_id'] = history.idx
                response_data['is_successful'] = True
        else:
            #transaction was declined
            response_data['is_successful'] = False
            #transaction was declined, cancel appointment
            # TODO: Notification disabled for now 3.4.22, Alejandro will come back to this in NRV-2786
            # cancel_telehealth_appointment(booking)
            #
            # #create notification for failed payment
            # start_time = LookupBookingTimeIncrements.query \
            #     .filter_by(idx=booking.booking_window_id_start_time).one_or_none().start_time
            # payment_last_four = PaymentMethods.query \
            #     .filter_by(idx=booking.payment_method_id).one_or_none().number
            # create_notification(booking.client_user_id,
            #                     3, 
            #                     5, 
            #                     "Your Card Could Not Be Charged", 
            #                     f"Your telehealth appointment with {booking.practitioner.firstname} \
            #                     {booking.practitioner.lastname} at {start_time} on {booking.target_date}, \
            #                     unfortunately, had to be canceled as your payment method ending in \
            #                     {payment_last_four} could not be charged. Please revise your payment \
            #                     method or perhaps speak with your bank to resolve the issue")
        return response_data


    def charge_telehealth_booking(self, booking: TelehealthBookings):
        """
        Charge a user for their telehealth appointment

        Params
        ------
        booking : TelehealthBookings

        Returns
        ------
        dict : instamed response
        """

        professional_role = LookupRoles.query.filter_by(role_name = booking.profession_type).one_or_none().display_name
        professional_role = professional_role.replace(" ", "")
        transaction_descriptor = f"Telehealth-{professional_role}-{booking.scheduled_duration_mins}mins"
        payment_data = self.charge_user(
            user_id = booking.client_user_id, 
            payment_method_id = booking.payment_method_id, 
            amount = str(booking.consult_rate), 
            transaction_descriptor = transaction_descriptor)

        if not payment_data['is_successful']:
            cancel_telehealth_appointment(booking)
            return payment_data
        elif payment_data.get('is_partially_approved'):
            cancel_telehealth_appointment(booking)
            payment_data['message'] = "Partial payment received. Appointment has been canceled and partial payment has been voided"
            db.session.commit()
            return payment_data, 400

        booking.charged = True
        booking.payment_history_id = payment_data['payment_history_id']

        db.session.commit()

        return payment_data


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

    # ensure that cancellation request does not occur during or after the scheduled meeting time
    booking_start_time = datetime.combine(
            date=booking.target_date_utc,
            time = LookupBookingTimeIncrements.query.filter_by(idx = booking.booking_window_id_start_time_utc).one_or_none().start_time)

    current_time_utc = datetime.utcnow()
    
    # prevent bookings that have already started from being cancelled. 
    # exception: practitioner no show triggered by background process
    if current_time_utc > booking_start_time and reason != 'Practitioner No Show':
        raise BadRequest('Unable to cancel booking. Schedueld meeting has already begun')
    
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
        history = PaymentHistory.query.filter_by(idx=booking.payment_history_id).one_or_none()
        if history:
            #first attempt to void, if that fails payment was likely more than 24 hours ago
            #in which case we should refund instead of void
            im = Instamed()
            try:
                im.void_payment(history.idx, reason)
            except:
                im.refund_payment(history, booking.consult_rate, reason)

    #TODO: Create notification/send email(?) to user that their appointment 

    db.session.commit()
    return