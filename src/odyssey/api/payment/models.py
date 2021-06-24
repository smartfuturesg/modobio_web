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