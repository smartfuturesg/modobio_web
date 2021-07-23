"""
Database tables for the practitioner system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Practitioner'.
"""

from odyssey import db
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx, UserIdFkeyMixin

class PractitionerOrganizationAffiliation(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Table to hold data pertaining to practitioner's organization affiliations

    """

    organization_idx = db.Column(db.Integer, db.ForeignKey('LookupOrganizations.idx'), nullable=False)
    """
    index of the organization the practitioner is affiliated with

    :type: int, foreign key to :attr:`LookupOrganizations.org_id <odyssey.models.lookup.LookupOrganizations.org_id>`
    """

    org_info = db.relationship('LookupOrganizations', uselist=False, back_populates='practitioners_assigned')
    """
    Many to one relationship with Lookup Organizations table
    
    :type: :class:`LookupOrganizations` instance 
    """
