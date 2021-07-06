"""
Database tables for the client intake portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``Client``.
"""
import base64
import os
import pytz
import random
import secrets

from datetime import datetime, timedelta
from hashlib import md5
from sqlalchemy import text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from odyssey.utils.constants import DB_SERVER_TIME, ALPHANUMERIC
from odyssey.utils.base.models import BaseModelWithIdx, UserIdFkeyMixin, BaseModel
from odyssey import db

phx_tz = pytz.timezone('America/Phoenix')


class ClientInfo(BaseModel):
    """ Client information table

    This table stores general information of a client.
    """

    __searchable__ = ['dob']

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), primary_key=True, nullable=False)
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """
    
    membersince = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Member since date

    The date a client was first added to the system

    :type: datetime
    """

    guardianname = db.Column(db.String(100))
    """
    Name of client's parent or guardian, if applicable.

    :type: str, max length 50
    """

    guardianrole = db.Column(db.String(50))
    """
    Parent or guardian's role to the client.

    :type: str, max length 50
    """

    state = db.Column(db.String(2))
    """
    Client address state.

    Currently only US States. Defaults to AZ.

    :type: str, max length 2
    """

    country = db.Column(db.String(2))
    """
    Client address country.

    Currently defaults to US.

    :type: str, max length 2
    """

    preferred = db.Column(db.SmallInteger)
    """
    Client preferred contact method.

    :type: int, smallint, signed int16
    """

    emergency_contact = db.Column(db.String(50))
    """
    Client emergency contact name.

    :type: str, max length 50
    """

    emergency_phone = db.Column(db.String(20))
    """
    Client emergency contact phone number.

    :type: str, max length 20
    """

    healthcare_contact = db.Column(db.String(50))
    """
    Client primary healthcare provider name.

    :type: str, max length 50
    """

    healthcare_phone = db.Column(db.String(20))
    """
    Client primary health care provider phone number.

    :type: str, max length 20
    """

    gender = db.Column(db.String(1))
    """
    Client gender.

    :type: str, max length 1
    """

    dob = db.Column(db.Date)
    """
    Client date of birth.

    :type: :class:`datetime.date`
    """

    height = db.Column(db.Integer)
    """
    Most recently reported height in cm.

    :type: int
    """

    weight = db.Column(db.Integer)
    """
    Most recently reported weight in g.

    :type: int
    """

    waist_size = db.Column(db.Integer)
    """
    Most recently reported waist size in cm.

    :type: int
    """

    profession = db.Column(db.String(100))
    """
    Client profession.

    :type: str, max length 100
    """

    receive_docs = db.Column(db.Boolean)
    """
    Indicates whether or not client wants to receive a copy of the signed documents.

    :type: bool
    """
    
    primary_goal_id = db.Column(db.Integer, db.ForeignKey('LookupGoals.goal_id'))
    """
    The client's stated primary goal for using modobio. Must be an option in the LookupGoals table.

    :type: int, foreign key('LookupGoal.goal_id')
    """

    primary_macro_goal_id = db.Column(db.Integer, db.ForeignKey('LookupMacroGoals.goal_id'), nullable=True)
    """
    The client's primary goal for using modobio. Must be an option in the LookupMacroGoals table.

    :type: int, foreign key('LookupMacroGoals.goal_id')
    """

    primary_goal_description = db.Column(db.String(300), nullable=True)
    """
    The client's description of primary goal for using modobio. Optional

    :type: str, max length 300 
    """

    primary_pharmacy_name = db.Column(db.String)
    """
    Primary Pharmacy Name

    :type: str
    """

    primary_pharmacy_address = db.Column(db.String)
    """
    Primary Pharmacy address

    :type: str
    """

    profile_pictures = db.relationship('UserProfilePictures', uselist=True, back_populates='client_info')
    """
    One to many relationship with UserProfilePictures

    :type: :class:`UserProfilePicture` instance
    """


    def client_info_search_dict(self, user) -> dict:
        """ Searchable client info.
        
        Returns a subset of the data in this row object.
        The returned dict contains the following keys:

        - user_id
        - firstname
        - lastename
        - dob (date of birth)
        - phone
        - email

        Returns
        -------
        dict
            Subset of data in this row object.
        """
        data = {
            'user_id': self.user_id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'dob': self.dob,
            'phone': user.phone_number,
            'email': user.email
        }
        return data

    @staticmethod
    def all_clients_dict(query: Query, page: int, per_page: int, **kwargs) -> tuple:
        """ Paginate a search in this table.
        
        Given a search query in this table, return the results for page ``page``
        with ``per_page`` results per page. The returned result itmes are generated
        by :meth:`client_info_search_dict`.

        Parameters
        ----------
        query : :class:`sqlalchemy.orm.query.Query`
            The SQL query with a (possibly) long list of results to paginate.

        page : int
            The current page to display results for.

        per_page : int
            How many results to display per page.

        Returns
        -------
        dict
            A dictionary with ``items``, a list of dicts containing the search results,
            and ``_meta`` a dict containing pagination information.

        :class:`flask_sqlalchemy.Pagination`
            An object holding the paginated search results from the SQLAlchemy query.
        """
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.client_info_search_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
                }
            }
        return data, resources

@db.event.listens_for(ClientInfo, "after_update")
def update_dob(mapper, connection, target):
    """ 
    Listens for any updates to ClientInfo table
    """
    from odyssey.utils.search import update_client_dob
    update_client_dob(target.user_id, target.dob)

class ClientRaceAndEthnicity(BaseModelWithIdx, UserIdFkeyMixin):
    """ Holds information about the race and ethnicity of a client's parents """

    is_client_mother = db.Column(db.Boolean, nullable=False)
    """
    Denotes if this information pertains to the user's mother or father

    :type: boolean
    """

    race_id = db.Column(db.ForeignKey('LookupRaces.race_id', ondelete="CASCADE"), nullable=False)
    """
    Foreign key from LookupRaces table.

    :type: int, foreign key to :attr:'LookupRaces.race_id <odyssey.models.lookup.LookupRaces.race_id>'
    """

class ClientFacilities(BaseModelWithIdx, UserIdFkeyMixin):
    """ A mapping of client ID number to registered facility ID numbers. """
    
    facility_id = db.Column(db.ForeignKey('RegisteredFacilities.facility_id',ondelete="CASCADE"), nullable=False)
    """
    RegisteredFacilities ID number.

    :type: int, foreign key to :attr:`RegisteredFacilities.facility_id`
    """

class ClientConsent(BaseModelWithIdx, UserIdFkeyMixin):
    """ Client consent form table

    This table stores the signature and related information of the consent form.
    """

    displayname = 'Consent form'
    """
    Print-friendly name of this document.

    :type: str
    """

    current_revision = '20200317'
    """
    Current revision of this document.

    The revision string is updated whenever the contents of the document change. The
    revision string can be anything, but it typically consists of the ISO formatted
    date (e.g. 20200519).

    :type: str
    """

    infectious_disease = db.Column(db.Boolean)
    """
    Indicates whether or not client ever had an infectious disease.

    :type: bool
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

    :type: :class:`datetime.date`
    """

    signature = db.Column(db.Text)
    """
    Signature.

    Stored as a base64 encoded png image, prefixed with mime-type.

    :type: str
    """

    revision = db.Column(db.String(10))
    """
    Revision string of the latest signed document.

    The revision string is updated whenever the contents of the document change.
    The revision stored here is the revision of the newest signed document.

    :type: str, max length 10
    """

    pdf_path = db.Column(db.String(200))
    """
    Path where signed document is stored as a PDF file.

    :type: str, max length 200
    """

    pdf_hash = db.Column(db.String(40))
    """
    SHA-1 hash (as a hexadecimal string) of the stored PDF file.

    :type: str, max length 40
    """

class ClientRelease(BaseModelWithIdx, UserIdFkeyMixin):
    """ Client release of information table

    This table stores the signature and related information of the
    release of information form.
    """

    displayname = 'Release of information form'
    """
    Print-friendly name of this document.

    :type: str
    """

    current_revision = '20200416'
    """
    Current revision of this document.

    The revision string is updated whenever the contents of the document change. The
    revision string can be anything, but it typically consists of the ISO formatted
    date (e.g. 20200519).

    :type: str
    """

    release_of_all = db.Column(db.Boolean)
    """
    Indicates whether or not client want to allow to release all protected health information.

    :type: bool
    """

    release_of_other = db.Column(db.String(1024))
    """
    Describes what other protected health information can be released.

    :type: str, max length 1024
    """

    release_date_from = db.Column(db.Date)
    """
    Limits the release of protected health information to from this date.

    :type: :class:`datetime.date`
    """

    release_date_to = db.Column(db.Date)
    """
    Limits the release of protected health information to until this date.

    :type: :class:`datetime.date`
    """

    release_purpose = db.Column(db.String(1024))
    """
    Describes for what purpose protected health information can be released.

    :type: str, max length 1024
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

    :type: :class:`datetime.date`
    """

    signature = db.Column(db.Text)
    """
    Signature.

    Stored as a base64 encoded png image, prefixed with mime-type.

    :type: str
    """

    revision = db.Column(db.String(10))
    """
    Revision string of the latest signed document.

    The revision string is updated whenever the contents of the document change.
    The revision stored here is the revision of the newest signed document.

    :type: str, max length 10
    """

    pdf_path = db.Column(db.String(200))
    """
    Path where signed document is stored as a PDF file.

    :type: str, max length 200
    """

    pdf_hash = db.Column(db.String(40))
    """
    SHA-1 hash (as a hexadecimal string) of the stored PDF file.

    :type: str, max length 40
    """

class ClientPolicies(BaseModelWithIdx, UserIdFkeyMixin):
    """ Client policies table

    This table stores the signature and related information of the
    Modo Bio policies form.
    """

    displayname = 'Policies form'
    """
    Print-friendly name of this document.

    :type: str
    """

    current_revision = '20200513'
    """
    Current revision of this document.

    The revision string is updated whenever the contents of the document change. The
    revision string can be anything, but it typically consists of the ISO formatted
    date (e.g. 20200519).

    :type: str
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

    :type: :class:`datetime.date`
    """

    signature = db.Column(db.Text)
    """
    Signature.

    Stored as a base64 encoded png image, prefixed with mime-type.

    :type: str
    """

    revision = db.Column(db.String(10))
    """
    Revision string of the latest signed document.

    The revision string is updated whenever the contents of the document change.
    The revision stored here is the revision of the newest signed document.

    :type: str, max length 10
    """

    pdf_path = db.Column(db.String(200))
    """
    Path where signed document is stored as a PDF file.

    :type: str, max length 200
    """

    pdf_hash = db.Column(db.String(40))
    """
    SHA-1 hash (as a hexadecimal string) of the stored PDF file.

    :type: str, max length 40
    """

class ClientConsultContract(BaseModelWithIdx, UserIdFkeyMixin):
    """ Client initial consultation contract table

    This table stores the signature and related information for the
    initial consultation contract.
    """

    displayname = 'Consultation contract'
    """
    Print-friendly name of this document.

    :type: str
    """

    current_revision = '20200428'
    """
    Current revision of this document.

    The revision string is updated whenever the contents of the document change. The
    revision string can be anything, but it typically consists of the ISO formatted
    date (e.g. 20200519).

    :type: str
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

    :type: :class:`datetime.date`
    """

    signature = db.Column(db.Text)
    """
    Signature.

    Stored as a base64 encoded png image, prefixed with mime-type.

    :type: str
    """

    revision = db.Column(db.String(10))
    """
    Revision string of the latest signed document.

    The revision string is updated whenever the contents of the document change.
    The revision stored here is the revision of the newest signed document.

    :type: str, max length 10
    """

    pdf_path = db.Column(db.String(200))
    """
    Path where signed document is stored as a PDF file.

    :type: str, max length 200
    """

    pdf_hash = db.Column(db.String(40))
    """
    SHA-1 hash (as a hexadecimal string) of the stored PDF file.

    :type: str, max length 40
    """

class ClientSubscriptionContract(BaseModelWithIdx, UserIdFkeyMixin):
    """ Client subscription contract table

    This table stores the signature and related information for the
    subscription contract.
    """

    displayname = 'Subscription contract'
    """
    Print-friendly name of this document.

    :type: str
    """

    current_revision = '20200428'
    """
    Current revision of this document.

    The revision string is updated whenever the contents of the document change. The
    revision string can be anything, but it typically consists of the ISO formatted
    date (e.g. 20200519).

    :type: str
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

    :type: :class:`datetime.date`
    """

    signature = db.Column(db.Text)
    """
    Signature.

    Stored as a base64 encoded png image, prefixed with mime-type.

    :type: str
    """

    revision = db.Column(db.String(10))
    """
    Revision string of the latest signed document.

    The revision string is updated whenever the contents of the document change.
    The revision stored here is the revision of the newest signed document.

    :type: str, max length 10
    """

    pdf_path = db.Column(db.String(200))
    """
    Path where signed document is stored as a PDF file.

    :type: str, max length 200
    """

    pdf_hash = db.Column(db.String(40))
    """
    SHA-1 hash (as a hexadecimal string) of the stored PDF file.

    :type: str, max length 40
    """

class ClientIndividualContract(BaseModelWithIdx, UserIdFkeyMixin):

    displayname = 'Individual services contract'
    """
    Print-friendly name of this document.

    :type: str
    """

    current_revision = '20200513'
    """
    Current revision of this document.

    The revision string is updated whenever the contents of the document change. The
    revision string can be anything, but it typically consists of the ISO formatted
    date (e.g. 20200519).

    :type: str
    """

    doctor = db.Column(db.Boolean, default=False)
    """
    Indicates whether or not client wants to buy a doctor's appointment.

    :type: bool
    """

    pt = db.Column(db.Boolean, default=False)
    """
    Indicates whether or not client wants to buy a physical therapy session.

    :type: bool
    """

    data = db.Column(db.Boolean, default=False)
    """
    Indicates whether or not client wants to buy a data tracking and analysis package.

    :type: bool
    """

    drinks = db.Column(db.Boolean, default=False)
    """
    Indicates whether or not client wants to buy nutritional supplements.

    :type: bool
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

    :type: :class:`datetime.date`
    """

    signature = db.Column(db.Text)
    """
    Signature.

    Stored as a base64 encoded png image, prefixed with mime-type.

    :type: str
    """

    revision = db.Column(db.String(10))
    """
    Revision string of the latest signed document.

    The revision string is updated whenever the contents of the document change.
    The revision stored here is the revision of the newest signed document.

    :type: str, max length 10
    """

    pdf_path = db.Column(db.String(200))
    """
    Path where signed document is stored as a PDF file.

    :type: str, max length 200
    """

    pdf_hash = db.Column(db.String(40))
    """
    SHA-1 hash (as a hexadecimal string) of the stored PDF file.

    :type: str, max length 40
    """

class ClientReleaseContacts(BaseModelWithIdx, UserIdFkeyMixin):
    """ Contact information for the release form.

    This table stores contact information for :attr:`ClientRelease.release_to`.
    """

    release_contract_id = db.Column(db.Integer, db.ForeignKey('ClientRelease.idx',ondelete="CASCADE"), nullable=False)
    """
    Index of the :class:``ClientRelease`` table.

    :type: int, foreign key to :attr:`ClientRelease.idx`
    """

    release_direction = db.Column(db.String, nullable=False)
    """
    Direction of medical data release.

    A client can release medical data to someone, or release someone else's data.
    This variable indicates the direction of the release. Must be either ``to`` or
    ``from``.

    :type: str
    """

    name = db.Column(db.String, nullable=False)
    """
    Full name of the contact.

    :type: str
    """

    email = db.Column(db.String, nullable=True)
    """
    Email address of the contact.

    :type: str
    """

    phone = db.Column(db.String, nullable=True)
    """
    Phone number of the contact.

    :type: str
    """

    relationship = db.Column(db.String, nullable=True)
    """
    Relationship of the client with the contact.

    :type: str
    """

class ClientClinicalCareTeam(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    Stores emails and user_ids of clinical care team members.
    Each client may have a maximum of 6 clinical care team members. These are 
    individuals who are authorized on behalf of the client to view 
    certain clinical data.     
    """

    team_member_email = db.Column(db.String, nullable=True)
    """
    Deprecated 6.11.21 - all care team members will be registered users. No need to log emails
    Email address of the clinical care team member.

    :type: str
    """

    team_member_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=True)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    is_temporary = db.Column(db.Boolean, default=False)
    """
    Denotes if this team member has temporary access. This is used to give professionals access for
    a limited time prior to a scheduled telehealth appointment. Temporary team members will not count
    towards a client's maximum allowed.

    :type: bool
    """

class ClientMobileSettings(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Holds the values for mobile settings that users have enabled or disabled
    """

    use_24_hour_clock = db.Column(db.Boolean())
    """
    Time format preferred by the user, true for 24 hr clock, false for 12 hr

    :type: boolean
    """

    date_format = db.Column(db.String())
    """
    Date format preferred by the user, options are:

    %d-%b-%Y ( 14-Mar-2020 )
    %b-%d-%Y ( Mar-14-2020 )
    %d/%m/%Y ( 14/05/2020 )
    %m/%d/%Y ( 05/14/2020 )

    :type: string
    """

    include_timezone = db.Column(db.Boolean())
    """
    Denotes if timezone name should be included with the time

    :type: boolean
    """

    biometrics_setup = db.Column(db.Boolean())
    """
    Denotes if user has setup biometric login and wishes to use it

    :type: boolean
    """

    timezone_tracking = db.Column(db.Boolean())
    """
    Denotes if the user wishes to enable timezone tracking

    :type: Boolean
    """

    is_right_handed = db.Column(db.Boolean())
    """
    Denotes if user is right-handed

    :type: boolean
    """

    display_middle_name = db.Column(db.Boolean())
    """
    Denotes if the user would like their middle name to be displayed

    :type: boolean
    """

    enable_push_notifications = db.Column(db.Boolean())
    """
    Denotes if user has enabled push notifications

    :type: boolean
    """
    
class ClientAssignedDrinks(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Stores information about what nutrional beverages a client has been assigned.
    Clients will only see drinks that have been assigned to them when viewing
    the selection of nutritional beverages. Drinks can be assigned to a client
    either automatically based on their goals or manually by staff members.
    """

    drink_id = db.Column(db.Integer, db.ForeignKey('LookupDrinks.drink_id', ondelete="CASCADE"), nullable=False)
    """
    Id of the drink for this assignment.

    :type: int, foreign key('LookupDrinks.drink_id)
    """

class ClientHeightHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Stores historical height measurements of clients.
    """

    height = db.Column(db.Integer)
    """
    Value for this height measurement in cm.

    :type: int
    """

class ClientWeightHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Stores historical weight measurements of clients.
    """

    weight = db.Column(db.Integer)
    """
    Value for this weight measurement in g.

    :type: int
    """

class ClientWaistSizeHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """
    Stores historical waist size measurements of clients.
    """

    waist_size = db.Column(db.Integer)
    """
    Value for this waist size measurement in cm.

    :type: int
    """
    
class ClientClinicalCareTeamAuthorizations(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    DEPRECATED - 6.30.21
    TODO: remove

    Stores clinical care team authorizations.
    One line per user, team memmber, resource combinaiton. Resource IDs come from 
    the LookupCareTeamTables table    
      
    """

    __table_args__ = (UniqueConstraint('user_id', 'team_member_user_id', 'resource_id', name='care_team_auth_unique_resource_user_team_member_ids'),)

    team_member_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number of the clinical care team member. Only modobio users may be entered into this table. With that, team members must
    be signed up as a user in order to recieve care team data from modobio. 

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    resource_id = db.Column(db.Integer, db.ForeignKey('LookupClinicalCareTeamResources.resource_id',ondelete="CASCADE"), nullable=False)
    """
    Resource ID refers back to the care team resources table which stores the tables that can be accessed by care team members

    :type: int, foreign key to :attr:`LookupClinicalCareTeamResources.resource_id <odyssey.models.lookup.LookupClinicalCareTeamResources.resource_id>`
    """

    status = db.Column(db.String())
    """
    Status of data access request
    
    ("pending","approved")
    NOTE: "rejected" is not in the list above because rejected would just be deleted

    :type: str
    """
    
class ClientTransactionHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    Stores history of client transactions
    """

    date = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Date of this transaction.

    :type: :class:'datetime.datetime'
    """

    category = db.Column(db.String)
    """
    Transaction category, comes from LookupTransactionTypes table.

    :type: string
    """

    name = db.Column(db.String)
    """
    Transaction name, comes from LookupTransactionTypes table.

    :type: string
    """

    price = db.Column(db.Float)
    """
    Price of this transaction, comes from LookupTransactionTypes table.

    :type: float
    """

    currency = db.Column(db.String)
    """
    Name of the currency used for this transaction.

    :type: string
    """

    payment_method = db.Column(db.String)
    """
    Method that the client used to pay for this transaction. Card type (Visa, Mastercard etc.) and last 4 digits.

    :type: string
    """

class ClientPushNotifications(BaseModelWithIdx, UserIdFkeyMixin):
    """
    This table holds the categories of push notifications that a user has enabled.
    If a notification type appears in this table for a user id, it means that user has this
    type of notification enabled.
    """

    notification_type_id = db.Column(db.Integer, db.ForeignKey('LookupNotifications.notification_type_id', ondelete="CASCADE"), nullable=False)
    """
    Denotes what type of notification this is as defined in the LookupNotifications table.

    :type: int, foreign key('LookupNotifications.notification_id')
    """

class ClientDataStorage(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    Details on how much data storage each client is using
      
    """

    storage_tier = db.Column(db.String)
    """
    client storage tier

    :type: str
    """

    total_bytes = db.Column(db.Float)
    """
    Bytes stored by client
    
    :type: float
    """

class ClientEHRPageAuthorizations(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    Stores EHR page authorizations granted by clients to other modobio users. 

    EHR page authorization options are found in LookupEHRPages

    """

    __table_args__ = (UniqueConstraint('user_id', 'team_member_user_id', 'resource_group_id', name='ehr_page_auth_unique_resource_user_team_member_ids'),)

    team_member_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number of the care team member. 

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    resource_group_id = db.Column(db.Integer, db.ForeignKey('LookupEHRPages.resource_group_id',ondelete="CASCADE"), nullable=False)
    """
    Resource group ID refers to a grouping of electronic health record resources found on a given page in the application.  

    :type: int, foreign key to :attr:`LookupEHRPages.resource_group_id <odyssey.models.lookup.LookupEHRPages.resource_group_id>`
    """

    status = db.Column(db.String())
    """
    Status of data access request
    
    ("pending","approved")
    NOTE: "rejected" is not in the list above because rejected would just be deleted

    :type: str
    """
