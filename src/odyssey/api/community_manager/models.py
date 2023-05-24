"""
Database tables for the client intake portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``Client``.
"""
import logging

logger = logging.getLogger(__name__)

from odyssey import db
from odyssey.utils.base.models import BaseModel


class CommunityManagerSubscriptionGrants(BaseModel):
    """Community Manager Subscription Grants. Stores details related to subscription grant requests"""

    __tablename__ = 'CommunityManagerSubscriptionGrants'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('User.user_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )

    email = db.Column(db.String)
    """
    Email of the user being granted a subscription. May or may not be tied to an account at the time of subscription grant.
    
    :type: string
    """

    subscription_grantee_user_id = db.Column(
        db.Integer,
        db.ForeignKey('User.user_id', ondelete='CASCADE'),
        nullable=True,
    )
    """
    ModoBio ID of the user being granted a subscription. 

    :type: string
    """

    subscription_type_id = db.Column(db.Integer, db.ForeignKey('LookupSubscriptions.sub_id'))
    """
    Id of this subscription plan. Comes from the LookupSubscriptions table.

    :type: int, foreign key('LookupSubscriptions.sub_id')
    """

    sponsor = db.Column(db.String(75), nullable=False)
    """
    Institutional affiliation of the subscription granter.

    :type: str    
    """

    activated = db.Column(db.Boolean, default=False, nullable=False)
    """
    Whether or not this subscription grant has been activated.
    :type: bool
    """

    subscription = db.relationship('UserSubscriptions', back_populates='sponsorship', uselist=False)

    subscription_type_information = db.relationship('LookupSubscriptions')
    """
    Relationship lookup subscriptions
    """
    def __repr__(self):
        return (
            f'<CommunityManagerSubscriptionGrants(user_id={self.user_id},'
            f' email={self.email},'
            f' subscription_type_id={self.subscription_type_id},'
            f' sponsor={self.sponsor}, activated={self.activated})>'
        )
