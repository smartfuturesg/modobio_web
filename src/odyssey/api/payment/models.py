"""
Database tables for supporting miscellaneous functionality. 
"""

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.base.models import BaseModelWithIdx, UserIdFkeyMixin

class PaymentMethods(BaseModelWithIdx, UserIdFkeyMixin):
    """
    This table links user with their saved payment methods. 
    """

    payment_id = db.Column(db.String)
    """
    InstaMed payment id to reference when charging this method.

    :type: string
    """

    payment_type = db.Column(db.String)
    """
    Type of this payment. Options are 'Mastercard', 'Visa', 'American Express', and 'Discover'.

    :type: string
    """

    number = db.Column(db.Integer)
    """
    Last 4 digits of the card number for this payment method.

    :type: int
    """

    is_default = db.Column(db.Boolean)
    """
    Denotes if this method is the default payment method for this user.

    :type: boolean
    """

class PaymentStatus(BaseModelWithIdx, UserIdFkeyMixin):

    alias

    card_present_status

    current_transaction_status_code

    merchant_id

    original_transaction_id

    original_transaction_status_code

    payment_transaction_id

    request_amount

    save_on_file_transaction_id

    statement_id

    store_id
    
    terminal_id

    transaction_action

    user_id