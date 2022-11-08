"""
Database tables for the practitioner system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Practitioner'.
"""
import logging
logger = logging.getLogger(__name__)

from odyssey import db
from odyssey.utils.base.models import BaseModelWithIdx, UserIdFkeyMixin

class ProviderRoleRequests(BaseModelWithIdx,UserIdFkeyMixin):
    """ Table for storing role requests made by prospective providers. """

    role_id = db.Column(db.Integer, db.ForeignKey('LookupRoles.idx'), nullable=False)

    status = db.Column(db.String(10), nullable=False, default='inactive')
    """
    Status of the role request. Modobio staff will be responsible for
    updating this field with the appropriate status.

    Possible values are:
        - inactive
        - pending
        - rejected
        - granted

    :type: string
    """

    role_info = db.relationship('LookupRoles', uselist=False, foreign_keys='ProviderRoleRequests.role_id')
    """
    Many to one relationship with Lookup Roles table
    :type: :class:`LookupRoles` instance 
    """

    reviewer_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="SET NULL"), nullable=True)