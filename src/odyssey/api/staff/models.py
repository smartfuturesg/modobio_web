"""
Database tables staff member information for the Modo Bio Staff application.
All tables in this module are prefixed with ``Staff``.
"""
import logging
from sqlalchemy.sql.expression import except_all
logger = logging.getLogger(__name__)

from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx, UserIdFkeyMixin
from odyssey.api.lookup.models import LookupRoles

class StaffProfile(BaseModel):
    """ Staff member profile information table.

    This table stores information regarding Modo Bio
    staff member profiles.
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), primary_key=True, nullable=False)
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    user_info = db.relationship('User', back_populates='staff_profile', foreign_keys='StaffProfile.user_id')
    """
    One-to-One relatinoship with User

    :type: :class: `User` instance
    """

    membersince = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Member since date

    The date a staff member was first added to the system

    :type: datetime
    """

    bio = db.Column(db.String)
    """
    staff member profile biography

    :type: string
    """

    profile_pictures = db.relationship('UserProfilePictures', uselist=True, back_populates='staff_profile')
    """
    One to many relationship with UserProfilePictures

    :type: :class:`UserProfilePicture` instance
    """

class StaffRecentClients(db.Model):
    """this table stores the last 10 clients that a staff member has loaded"""

    __tablename__ = 'StaffRecentClients'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    staff_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    User_id of the staff member that loaded the client

    :type: int, foreign key
    """

    client_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    User_id of the client that was loaded

    :type: int, foreign key
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp denoting when the staff member last loaded the client

    :type: datetime
    """

class StaffRoles(BaseModelWithIdx, UserIdFkeyMixin):
    """ Stores informaiton on staff role assignments. 

    Roles must be verified either by a manual or automatic internal review process.
    Some roles will be location based where verification is required for each locality
    (state, country etc.). 
    """

    role = db.Column(db.String, db.ForeignKey('LookupRoles.role_name'), nullable=False)
    """
    Name of the role assignment

    Possible roles include:

    -staff_admin
    -system_admin
    -client_services
    -physical_therapist
    -trainer
    -data_scientist
    -doctor
    -nutrition
    
    :type: str
    """

    role_info = db.relationship('LookupRoles', uselist=False, back_populates='professionals_assigned', foreign_keys='StaffRoles.role')
    """
    Many to one relationship with Lookup Roles table
    :type: :class:`LookupRoles` instance 
    """

    operational_territories = db.relationship('StaffOperationalTerritories', uselist=True, back_populates='role')
    """
    One to many relationship with staff's opeartional territories

    :type: :class:`StaffOperationalTerritories` instance list
    """ 

    credentials = db.relationship('PractitionerCredentials', uselist=True, back_populates='role')
    """
    One to many relationship with staff's opeartional territories

    :type: :class:`StaffOperationalTerritories` instance list
    """            

    granter_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=True)
    """
    ID of the user who granted this role to this user.

    Explicitly nullable to prevent a bootstrapping problem of adding the first staff member
    with a role to an empty database, which must be granted by another staff member who
    does not exist yet.

    :type: int, foreign key(User.user_id)
    """

    consult_rate = db.Column(db.Numeric(10,2))
    """
    Consultation rate for the practitioner

    :type: Numeric
    """

class StaffOperationalTerritories(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    Locations where staff members operate. Each entry is tied to a role in the StaffRoles table. 
    Depending on the profession, the role-territory paid must be verified with an active identification number
    or some other internal process. Verifications will be stored in another table. 

    """

    operational_territory_id = db.Column(db.Integer, db.ForeignKey('LookupTerritoriesOfOperations.idx'))
    """
    Operational subterritory from the operational territories lookup table.

    There will be an entry in this table for each role-operational_territory pair. For some professions, we will
    store verification IDs which may differ by sub_territory (e.g. medical doctors must have a different license to practice
    in each state).

    :type: int, foreign key to :attr:`LookupTerritoriesofOperation.idx <odyssey.models.lookup.LookupTerritoriesofOperation.idx>`
    """

    role_id = db.Column(db.Integer, db.ForeignKey('StaffRoles.idx', ondelete="CASCADE"), nullable=False)
    """
    Role from the StaffRoles table. 

    :type: int, foreign key to :attr:`StaffRoles.idx <odyssey.models.staff.StaffRoles.idx>`
    """

    role = db.relationship('StaffRoles', uselist=False, back_populates='operational_territories', foreign_keys='StaffOperationalTerritories.role_id')
    """
    Many to one relationship with staff roles table

    :type: :class:`StaffRoles` instance
    """

class StaffCalendarEvents(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    Model for events to be saved to the professional's calendar 
    """
    start_date = db.Column(db.Date, nullable=False)
    """
    If recurring, this is the recurrence start date,
    if not, this is the event start date

    :type: :class:`datetime.date`
    """

    end_date = db.Column(db.Date, nullable=True)
    """
    If event is recurring, this is the recurrence end date,
    if not, this is the event end date

    :type: :class:`datetime.date`
    """

    start_time = db.Column(db.Time, nullable=False)
    """
    Event start time

    :type: :class:'datetime.time'
    """

    end_time = db.Column(db.Time, nullable=False)
    """
    Event end time

    :type: :class:'datetime.time'
    """

    timezone = db.Column(db.String, nullable=True)
    """
    Local time zone name, saved at event creation

    :type: str
    """

    duration = db.Column(db.Interval, nullable=True)
    """
    Event duration, only important for recurring events

    :type: datetime.timedelta
    """

    all_day = db.Column(db.Boolean, nullable=False)
    """
    Flag if event lasts all day or not

    :type: bool
    """

    recurring = db.Column(db.Boolean, nullable=False)
    """
    Flag to determine if this event is recurring

    :type: bool
    """

    recurrence_type = db.Column(db.String, nullable=True)
    """
    Type of recurrence for the event. Must be one of RECURRENCE_TYPE = ('Daily', 'Weekly', 'Monthly', 'Yearly')

    :type: str
    """

    location = db.Column(db.String(100), nullable=True)
    """
    Event's location
    
    :type: str
    """

    description = db.Column(db.Text, nullable=True)
    """
    Event's description

    :type: str
    """

    availability_status = db.Column(db.String, nullable=False)
    """
    Professional's availabilit status through the event
    Currently, only options are in constants.py -> EVENT_AVAILABILITY = ('Busy', 'Available')

    :type: str
    """

class StaffOffices(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Model for information regarding a staff member's office for DoseSpot integration.
    """

    street = db.Column(db.String)
    """
    Street address for this office.

    :type: str
    """

    city = db.Column(db.String(35))
    """
    City where this office resides.

    :type: str
    """

    zipcode = db.Column(db.String(20))
    """
    ZIP code where this office resides.

    :type: str
    """

    territory_id = db.Column(db.Integer, db.ForeignKey('LookupTerritoriesOfOperations.idx'))
    """
    Client address territory. Foreign key gives information about both the state/province/etc. as
    well as the country.

    :type: int, foreign key(LookupTerritoriesOfOperations.idx)
    """

    email = db.Column(db.String(100))
    """
    Email address used to contact this office.

    :type: str
    """

    fax = db.Column(db.String(20))
    """
    Fax number used by this office.

    :type: str
    """

    phone = db.Column(db.String(20))
    """
    Phone number used by this office.

    :type: str
    """

    phone_type = db.Column(db.String(7))
    """
    Type of phone the number belongs to. Options are: primary, cell, work, home, fax, night, beeper.

    :type: str
    """

# @db.event.listens_for(StaffOffices, "after_insert")
# def ds_onboard_practitioner(mapper, connection, target):
#     """ 
#     Listens for any updates to StaffOffice table

#     If any updates occur, we will try to automatically onboard that MD to to the DS platform
#     """
#     from odyssey.integrations.dosespot import DoseSpot
#     from odyssey.api.practitioner.models import PractitionerCredentials
#     from odyssey.api.dosespot.models import DoseSpotPractitionerID

#     verified_npi = PractitionerCredentials.query.filter_by(user_id=target.user_id,credential_type='npi',status='Verified').one_or_none()
#     ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=target.user_id).one_or_none()

#     if verified_npi and not ds_practitioner:
#         ds = DoseSpot()
#         ds.onboard_practitioner(target.user_id)    

# @db.event.listens_for(StaffOffices, "after_update")
# def ds_onboard_practitioner(mapper, connection, target):
#     """ 
#     Listens for any updates to StaffOffice table

#     If any updates occur, we will try to automatically onboard that MD to to the DS platform
#     """
#     from odyssey.integrations.dosespot import DoseSpot
#     from odyssey.api.practitioner.models import PractitionerCredentials
#     from odyssey.api.dosespot.models import DoseSpotPractitionerID

#     verified_npi = PractitionerCredentials.query.filter_by(user_id=target.user_id,credential_type='npi',status='Verified').one_or_none()
#     ds_practitioner = DoseSpotPractitionerID.query.filter_by(user_id=target.user_id).one_or_none()

#     if verified_npi and not ds_practitioner:
#         ds = DoseSpot()
#         ds.onboard_practitioner(target.user_id)   