"""
Database tables for the client intake portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``Client``.
"""
import logging
logger = logging.getLogger(__name__)

import pytz

from sqlalchemy import  UniqueConstraint
from sqlalchemy.orm.query import Query
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.base.models import BaseModelWithIdx, UserIdFkeyMixin, BaseModel
from odyssey import db

phx_tz = pytz.timezone('America/Phoenix')


class CommunityManagerSubscriptionGrants(BaseModelWithIdx):
    """ Community Manager Subscription Grants. Stores details related to subscription grant requests """

    __tablename__ = 'CommunityManagerSubscriptionGrants'

    user_id = db.Column(db.Integer,  db.ForeignKey('User.user_id', ondelete="CASCADE"), primary_key=True, nullable=False)

    email = db.Column(db.String)
    """
    Email of the user being granted a subscription. May or may not be tied to an account at the time of subscription grant.
    
    :type: string
    """

    subscription_grantee_user_id = db.Column(db.Integer,  db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable = True)
    """
    ModoBio ID of the user being granted a subscription. 

    :type: string
    """

    sponsor = db.Column(db.String(75), nullable=False)
    """
    Institutional affiliation of the subscription granter.

    :type: str    
    """

    subscription = db.relationship("UserSubscriptions", back_populates="sponsorship", uselist=False)
