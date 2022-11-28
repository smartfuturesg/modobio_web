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


class ProviderCredentials(BaseModelWithIdx,UserIdFkeyMixin):
    """ Medical Credentials table
    
    This table is used for storing the Medical Doctor's credentials
    """

    country_id = db.Column(db.Integer, db.ForeignKey('LookupCountriesOfOperations.idx'))
    """
    Country the MD is submitting credentials for (USA)

    :type: str
    """

    state = db.Column(db.String(2))
    """
    State the MD has medical license for
    
    :type: str
    """

    credential_type = db.Column(db.String)
    """
    (Can be found in constants)
    For Medical Doctor: <NPI, DEA, Medical License>

    :type: str
    """

    credentials = db.Column(db.String)
    """
    Staff Input values

    :type: str    
    """

    status = db.Column(db.String)
    """
    Verification Status <Pending Verification, Verified, Rejected, Expired>

    :type: str
    """

    role_id = db.Column(db.Integer, db.ForeignKey('StaffRoles.idx', ondelete="CASCADE"), nullable=True)
    """
    Role from the StaffRoles table. 

    :type: int, foreign key to :attr:`StaffRoles.idx <odyssey.models.staff.StaffRoles.idx>`

    """
    
    role = db.relationship('StaffRoles', uselist=False, back_populates='credentials')
    """
    Many to one relationship with staff roles table

    :type: :class:`StaffRoles` instance
    """

    expiration_date = db.Column(db.Date)
    """
    Not currently used; will be used for expiration date for the license

    :type: date
    """
    