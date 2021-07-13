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
    """
    This table tracks payment activities processed outside of ModoBio's platform.
    InstaMed will send payment events orignating on their platform (refunds, voids, declines, etc.) to a webhook.
    """

    card_present_status = db.Column(db.String)
    """
    Describes the method card information was received. Either PresentManualKey or NotPresentInternet.

    :type: string
    """

    current_transaction_status_code = db.Column(db.String)
    """
    Describes the current status of this payment. 	Possible values:
    C = Approved
    V = Voided
    CB = charge back
    RI = Returns
    SE = Settlement Error
    S = Settled
    D = Declined

    :type: string
    """

    original_transaction_id = db.Column(db.String)
    """
    ID of the original transaction as defined by InstaMed.

    :type: string
    """

    original_transaction_status_code = db.Column(db.String)
    """
    Describes the current status of the original transaction. 	Possible values:
    C = Approved
    V = Voided
    CB = charge back
    RI = Returns
    SE = Settlement Error
    S = Settled
    D = Declined

    :type: string
    """

    payment_transaction_id = db.Column(db.String)
    """
    ID of this transaction as defined by InstaMed.

    :type: string
    """

    request_amount = db.Column(db.Numeric(10,2), nullable=False)
    """
    Amount of this transaction in dollars.

    :type: string
    """

    save_on_file_transaction_id = db.Column(db.String)
    """
    ID of this transaction's SaveOnFile payment method as defined by InstaMed.

    :type: string
    """

    transaction_action = db.Column(db.String)
    """
    Type of this transaction.

    Possible values:
    Sale
    Chargeback
    Return
    Refund

    :type: string
    """