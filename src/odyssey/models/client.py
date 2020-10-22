"""
Database tables for the client intake portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Client'.
"""
import base64
import os
import pytz
import random
import secrets

from datetime import datetime, timedelta
from hashlib import md5
from sqlalchemy import text
from odyssey.constants import DB_SERVER_TIME, ALPHANUMERIC
from odyssey import db, whooshee

phx_tz = pytz.timezone('America/Phoenix')



@whooshee.register_model('dob', 'record_locator_id')
class ClientInfo(db.Model):
    """ Client information table

    This table stores general information of a client.
    """

    __tablename__ = 'ClientInfo'

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated

    :type: datetime
    """

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    autoincrementing primary key

    :type: int, primary key, autoincrement
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
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

    :type: datetime.date
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
    Record Locator ID

    name_hash = md5(bytes((data['firstname']+data['lastname']), 'utf-8')).hexdigest()
    data['record_locator_id'] = (data['firstname'][0]+data['lastname'][0]+str(data['user_id'])+name_hash[0:6]).upper()    

    :type: str, max length 10
    """

    @staticmethod
    def generate_record_locator_id(firstname, lastname, user_id):
        """medical record hash generation"""
        random.seed(user_id)
        rli_hash = "".join([random.choice(ALPHANUMERIC) for i in range(10)])
        return (firstname[0]+lastname[0]+rli_hash).upper()

    def client_info_search_dict(self):
        """returns just the searchable client info (name, email, number)"""
        user = User.query.filter_by(user_id=self.user_id).one_or_none()
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
    def all_clients_dict(query, page, per_page, **kwargs):
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
    """ A mapping of client ids to registered facility ids
    """

    __tablename__ = 'ClientFacilities'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable = False)
    """
    Foreign key from ClienInfo table

    :type: int, foreign key
    """
    
    facility_id = db.Column(db.ForeignKey('RegisteredFacilities.facility_id',ondelete="CASCADE"), nullable=False)
    """
    Foreign key from RegisteredFacilities table

    :type: int, foreign key
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
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number.

    :type: int, foreign key to :attr:`User.user_id`
    """

    infectious_disease = db.Column(db.Boolean)
    """
    Indicates whether or not client ever had an infectious disease.

    :type: bool
    """

    signdate = db.Column(db.Date)
    """
    Signature date. This is filled by the client upon signing the document. Therefore, we can assume that 
    this date is in their local timezone. 

    :type: datetime.date
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
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id`
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

    :type: datetime.date
    """

    release_date_to = db.Column(db.Date)
    """
    Limits the release of protected health information to until this date.

    :type: datetime.date
    """

    release_purpose = db.Column(db.String(1024))
    """
    Describes for what purpose protected health information can be released.

    :type: str, max length 1024
    """

    signdate = db.Column(db.Date)
    """
    Signature date. This is filled by the client upon signing the document. Therefore, we can assume that 
    this date is in their local timezone. 

    :type: datetime.date
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
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id`
    """

    signdate = db.Column(db.Date)
    """
    Signature date. This is filled by the client upon signing the document. Therefore, we can assume that 
    this date is in their local timezone. 

    :type: datetime.date
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
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id`
    """

    signdate = db.Column(db.Date)
    """
    Signature date. This is filled by the client upon signing the document. Therefore, we can assume that 
    this date is in their local timezone. 

    :type: datetime.date
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
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id`
    """

    signdate = db.Column(db.Date)
    """
    Signature date. This is filled by the client upon signing the document. Therefore, we can assume that 
    this date is in their local timezone. 

    :type: datetime.date
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
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id`
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
    Signature date. This is filled by the client upon signing the document. Therefore, we can assume that 
    this date is in their local timezone. 

    :type: datetime.date
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
    """ Client external medical record table

    This table stored medical record ids from external medical institutes. 
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
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id`
    """

    med_record_id = db.Column(db.String, nullable=False)
    """
    medical record id 
    :type: str
    """

    institute_id = db.Column(db.Integer, db.ForeignKey('MedicalInstitutions.institute_id', ondelete="CASCADE"), nullable=False)
    """
    medical institute id 

    :type: int, foreign key to :attr:`MedicalInstitutions.institute_id`
    """

class ClientReleaseContacts(db.Model):
    """ Client external medical record table

    This table stored medical record ids from external medical institutes. 
    """

    __tablename__ = 'ClientReleaseContacts'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    release_contract_id = db.Column(db.Integer, db.ForeignKey('ClientRelease.idx',ondelete="CASCADE"), nullable=False)
    """
    ID refering back to the signed contract in the ClientRelease table

    :type: int, foreign key to :attr:`ClientRelease.idx`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',ondelete="CASCADE"), nullable=False)
    """
    User ID number

    :type: int, foreign key to :attr:`User.user_id`
    """

    release_direction = db.Column(db.String, nullable=False)
    """
    Direction of client medical dta release. Must be either 'TO' or 'FROM'

    :type: str
    """

    name = db.Column(db.String, nullable=False)
    """
    Full name of the contact

    :type: str
    """

    email = db.Column(db.String, nullable=True)
    """
    Email of the contact 

    :type: str
    """

    phone = db.Column(db.String, nullable=True)
    """
    Email of the contact 

    :type: str
    """

    relationship = db.Column(db.String, nullable=True)
    """
    Relationship the client has with the contact 

    :type: str
    """

