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
from sqlalchemy import text
from sqlalchemy.orm.query import Query
from odyssey.constants import DB_SERVER_TIME, ALPHANUMERIC
from odyssey import db, whooshee

phx_tz = pytz.timezone('America/Phoenix')


# @whooshee.register_model('firstname', 'lastname', 'email', 'phone', 'dob', 'record_locator_id')
class ClientInfo(db.Model):
    """ Client information table

    This table stores general information of a client.
    """

    __tablename__ = 'ClientInfo'

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    autoincrementing primary key

    :type: int, primary key, autoincrement
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
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

    street = db.Column(db.String(50))
    """
    Client street address.

    :type: str, max length 50
    """

    city = db.Column(db.String(50))
    """
    Client address city.

    :type: str, max length 50
    """

    state = db.Column(db.String(2))
    """
    Client address state.

    Currently only US States. Defaults to AZ.

    :type: str, max length 2
    """

    zipcode = db.Column(db.String(10))
    """
    Client address zip code.

    :type: str, max length 10
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
    
    record_locator_id = db.Column(db.String(12))
    """
    Deprecated. Use User.modobio_id instead
    Medical decord Locator ID.

    See :meth:`generate_record_locator_id`.

    :type: str, max length 12
    """

    def client_info_search_dict(self, user) -> dict:
        """ Searchable client info.
        
        Returns a subset of the data in this row object.
        The returned dict contains the following keys:

        - user_id
        - record_locator_id
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
            'record_locator_id': self.record_locator_id,
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


class ClientFacilities(db.Model):
    """ A mapping of client ID number to registered facility ID numbers. """

    __tablename__ = 'ClientFacilities'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable = False)
    """
    Foreign key from User table

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """
    
    facility_id = db.Column(db.ForeignKey('RegisteredFacilities.facility_id',ondelete="CASCADE"), nullable=False)
    """
    RegisteredFacilities ID number.

    :type: int, foreign key to :attr:`RegisteredFacilities.facility_id`
    """

class ClientConsent(db.Model):
    """ Client consent form table

    This table stores the signature and related information of the consent form.
    """

    __tablename__ = 'ClientConsent'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number.

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

class ClientRelease(db.Model):
    """ Client release of information table

    This table stores the signature and related information of the
    release of information form.
    """

    __tablename__ = 'ClientRelease'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

class ClientPolicies(db.Model):
    """ Client policies table

    This table stores the signature and related information of the
    Modo Bio policies form.
    """

    __tablename__ = 'ClientPolicies'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

class ClientConsultContract(db.Model):
    """ Client initial consultation contract table

    This table stores the signature and related information for the
    initial consultation contract.
    """

    __tablename__ = 'ClientConsultContract'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

class ClientSubscriptionContract(db.Model):
    """ Client subscription contract table

    This table stores the signature and related information for the
    subscription contract.
    """

    __tablename__ = 'ClientSubscriptionContract'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

class ClientIndividualContract(db.Model):

    __tablename__ = 'ClientIndividualContract'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

class ClientExternalMR(db.Model):
    """ External medical records table.

    This table stores medical record ID numbers from external medical institutes. 
    """

    __tablename__ = 'ClientExternalMR'

    __table_args__ = (
        db.UniqueConstraint('user_id', 'med_record_id', 'institute_id'),)

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    med_record_id = db.Column(db.String, nullable=False)
    """
    Medical record id.

    This medical record ID comes from an external medical institution.

    :type: str, non-null, unique
    """

    institute_id = db.Column(db.Integer, db.ForeignKey('MedicalInstitutions.institute_id', ondelete="CASCADE"), nullable=False)
    """
    Medical institute id.

    :type: int, foreign key to :attr:`MedicalInstitutions.institute_id`
    """

class ClientReleaseContacts(db.Model):
    """ Contact information for the release form.

    This table stores contact information for :attr:`ClientRelease.release_to`.
    """

    __tablename__ = 'ClientReleaseContacts'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    release_contract_id = db.Column(db.Integer, db.ForeignKey('ClientRelease.idx',ondelete="CASCADE"), nullable=False)
    """
    Index of the :class:``ClientRelease`` table.

    :type: int, foreign key to :attr:`ClientRelease.idx`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

class ClientSurgeries(db.Model):
    """ History of client surgeries.

    """

    __tablename__ = 'ClientSurgeries'

    surgery_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique id of the surgery

    :type: int, primary key, autoincrementing
    """

    client_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    User id of the client that received this surgery

    :type: int, foreign key to User.user_id
    """

    reporter_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    """
    User id of the staff member that reported this surgery

    :type: int, foreign key to User.user_id
    """

    surgery_category = db.Column(db.String, nullable=False)
    """
    Category of this surgery, must be defined in Constant.py MEDICAL_CONDITIONS['Surgery']

    :type: string
    """

    date = db.Column(db.Date, nullable=False)
    """
    Date of this surgery

    :type: date
    """

    surgeon = db.Column(db.String)
    """
    Name of the surgeon who performed this surgery

    :type: string
    """

    institution = db.Column(db.String)
    """
    Name of the institution where this surgery took place

    :type: string
    """

    notes = db.Column(db.String)
    """
    Notes about this surgery from the reporting staff member

    :type: string
    """