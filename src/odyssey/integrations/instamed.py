import requests

from flask import current_app

from odyssey.utils.errors import GenericThirdPartyError
from odyssey.api.payment.models import PaymentHistory

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

    def add_payment_method(self, token, expiration):
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
            }
        }

        response = requests.post(self.url_base + '/payment/paymentplan',
                                headers=self.request_header,
                                json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            raise GenericThirdPartyError(response.status_code, response.text)

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
            "Amount": str(amount)
        }

        response = requests.post(self.url_base + '/payment/refund-simple',
                        headers=self.request_header,
                        json=request_data)
        
        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            raise GenericThirdPartyError(response.status_code, response.text)

        return response.json()

    def charge_user(self, transaction_id, amount):
        """
        Charge a user.
        InstaMed URI: /payment/sale


        Params
        ------
        transaction_id: (string)
            InstaMed ID for the transaction to be refunded
        
        amount: (string)
            amount of money to be charged
        
        Returns
        -------
        dict of information regarding the sale
        """
        breakpoint()
        request_data = {
            "Outlet": self.outlet,
            "PaymentMethod": "OnFile",
            "PaymentMethodID": str(payment.payment_id),
            "Amount": str(session_cost)
        }

        response = requests.post(self.url_base + '/payment/sale',
                        headers=self.request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            #transaction was not successful, store in PaymentFailedTransactions
            cancel_telehealth_appointment(booking)
            return

        #convert response data to json (python dict)
        response_data = response.json()

        #check if card was declined or partially approved
        #(this is not an error as checked above since 200 is returned from InstaMed)
        if response_data['TransactionStatus'] == 'C':
            if response_data['IsPartiallyApproved']:
                #refund partial amount and log as an unsuccessful payment
                self.refund_payment(payment.payment_id, response_data['PartialApprovalAmount'])

                #TODO: log if refund was unsuccessful

                cancel_telehealth_appointment(booking)
                return
            else:
                #transaction was successful, store in PaymentHistory
                history = PaymentHistory(**{
                    'user_id': booking.client_user_id,
                    'payment_method_id': booking.payment_method_id,
                    'transaction_id': response_data['TransactionID'],
                    'transaction_amount': session_cost,
                })
                db.session.add(history)
                booking.charged = True
                db.session.commit()
        else:
            #transaction was declined
            cancel_telehealth_appointment(booking)