import requests
from werkzeug.exceptions import BadRequest

from flask import current_app

from odyssey.utils.misc import cancel_telehealth_appointment
from werkzeug.exceptions import BadRequest
from odyssey.api.payment.models import PaymentHistory, PaymentMethods
from odyssey.api.user.models import User
from odyssey.utils.misc import cancel_telehealth_appointment

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
                "MerchantID": '894805',
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
    
    def refund_payment(self, transaction_id, amount):
        """
        Refund a payment.
        InstaMed URI: /payment/refund


        Params
        ------
        transaction_id: (string)
            InstaMed ID for the transaction to be refunded
        
        amount: (string)
            amount of money to be refunded
        
        Returns
        -------
        dict of information regarding the refund
        """
        request_data = {
            "Outlet": self.outlet,
            "TransactionID": str(transaction_id),
            "Amount": str(amount),
            "Patient": {
                "AccountNumber": User.query.filter_by(idx=booking.client_user_id).one_or_none().modobio_id
            }
        }

        response = requests.post(self.url_base + '/payment/refund-simple',
                        headers=self.request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'Instamed returned the following error: {response.text}')

        return response.json()

    def void_payment(self, booking):
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
        transaction_id = PaymentHistory.query.filter_by(booking_id=booking.idx).one_or_none().transaction_id
        if not transaction_id:
            raise BadRequest(f'No transaction exists for the booking with booking id {booking.idx}.')

        request_data = {
            "Outlet": self.outlet,
            "TransactionID": str(transaction_id),
            "Patient": {
                "AccountNumber": User.query.filter_by(idx=booking.client_user_id).one_or_none().modobio_id
            }
        }

        response = requests.post(self.url_base + '/payment/void',
                        headers=self.request_header,
                        json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            raise BadRequest(f'Instamed returned the following error: {response.text}')

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
                "AccountNumber": User.query.filter_by(idx=booking.client_user_id).one_or_none().modobio_id
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
                        "AccountNumber": User.query.filter_by(idx=booking.client_user_id).one_or_none().modobio_id
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
                        ' voiding a partial transaction.')

                cancel_telehealth_appointment(booking)
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