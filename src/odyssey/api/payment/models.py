"""
Database tables for supporting miscellaneous functionality. 
"""
import logging
logger = logging.getLogger(__name__)

from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.base.models import BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin

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

    :type: numeric
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

class PaymentHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """
    This keeps track of payments that have been charged to users.
    """

    payment_method = relationship("PaymentMethods", backref="PaymentHistory")
    """
    Relationship to PaymentMethods
    """

    payment_method_id = db.Column(db.Integer, db.ForeignKey('PaymentMethods.idx', ondelete='SET NULL'))
    """
    Foreign key to the payment method used for this payment.

    :type: int, foreignkey(PaymentMethods.idx)
    """
    
    transaction_id = db.Column(db.String)
    """
    Instamed transaction id to be provided for the purpose of refunds or voids.

    :type: string
    """

    transaction_amount = db.Column(db.Numeric(10,2), nullable=False)
    """
    Amount of this transaction in USD.

    :type: numeric
    """

class PaymentRefunds(BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin):
    """
    This table keeps track of refunds that have been issued as well as the staff member who 
    issued the refund.
    """

    __table_args__ = (
        CheckConstraint('char_length(refund_reason) > 20',
                        name='refund_reason_min_length'),
    )

    payment = relationship("PaymentHistory", backref="PaymentRefunds")
    """
    Relationship to the payment that was refunded in the PaymentHistory table.
    """

    payment_id = db.Column(db.Integer, db.ForeignKey('PaymentHistory.idx'))
    """
    Foreign key to the payment this refund is associated with

    :type: int, foreignkey(PaymentHistory.idx)
    """

    refund_amount = db.Column(db.Numeric(10,2), nullable=False)
    """
    Amount that was refunded in USD. Note that refunds can be partial, so they may not always be
    the full amount as seen in the original payment.

    :type: numeric
    """

    refund_reason = db.Column(db.String)
    """
    Reason this refund was issued as reported by the staff member that issued the refund.

    :type: string
    """