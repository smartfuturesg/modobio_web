"""
Database tables for the practitioner system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Practitioner'.
"""
import logging

logger = logging.getLogger(__name__)

from odyssey import db
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx, UserIdFkeyMixin


class PractitionerCredentials(BaseModelWithIdx, UserIdFkeyMixin):
    """Medical Credentials table

    This table is used for storing the Medical Doctor's credentials

    Deprecated 11.28.22
    All data from this table is migrated to ProviderCredentials
    """

    country_id = db.Column(db.Integer, db.ForeignKey("LookupCountriesOfOperations.idx"))
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

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("StaffRoles.idx", ondelete="CASCADE"),
        nullable=True,
    )
    """
    Role from the StaffRoles table. 

    :type: int, foreign key to :attr:`StaffRoles.idx <odyssey.models.staff.StaffRoles.idx>`

    """

    role = db.relationship("StaffRoles", uselist=False)
    """
    Many to one relationship with staff roles table

    :type: :class:`StaffRoles` instance
    """

    expiration_date = db.Column(db.Date)
    """
    Not currently used; will be used for expiration date for the license

    :type: date
    """


class PractitionerOrganizationAffiliation(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Table to hold data pertaining to practitioner's organization affiliations

    """

    organization_idx = db.Column(
        db.Integer, db.ForeignKey("LookupOrganizations.idx"), nullable=False
    )
    """
    index of the organization the practitioner is affiliated with

    :type: int, foreign key to :attr:`LookupOrganizations.org_id <odyssey.models.lookup.LookupOrganizations.org_id>`
    """

    affiliate_user_id = db.Column(db.String, nullable=True)
    """
    User identifier assigned by the affiliate organization. 
    
    :type: str
    """

    org_info = db.relationship(
        "LookupOrganizations",
        uselist=False,
        back_populates="practitioners_assigned",
    )
    """
    Many to one relationship with Lookup Organizations table
    
    :type: :class:`LookupOrganizations` instance 
    """
