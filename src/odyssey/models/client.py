"""
Database tables for the client intake portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Client'.
"""
import base64
import os
import pytz
import secrets

from datetime import datetime, timedelta
from hashlib import md5

from odyssey import db, whooshee

phx_tz = pytz.timezone('America/Phoenix')

# @whooshee.register_model('firstname','lastname','email','phone')
class GarbageClient(db.Model):
    
    __tablename__ = 'GarbageClient'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone = db.Column(db.String(20))

@whooshee.register_model('firstname','lastname','email','phone')
class ClientInfo(db.Model):
    """ Client information table

    This table stores general information of a client. The information is taken
    only once, during the initial consult. The primary index of this table is the
    :attr:`clientid` number. Many other tables in this database refer to the
    :attr:`clientid` number, so a new client **MUST** be added to this table first,
    in order to generate the :attr:`clientid` number.
    """

    __tablename__ = 'ClientInfo'

    # __searchable__ = ['firstname','lastname','email','phone']

    clientid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Client ID number

    The main identifier of a client throughout the Modo Bio system.

    :type: int, primary key, autoincrement
    """

    firstname = db.Column(db.String(50))
    """
    Client first name.

    :type: str, max length 50
    """

    middlename = db.Column(db.String(50))
    """
    Client middle name(s).

    :type: str, max length 50
    """

    lastname = db.Column(db.String(50))
    """
    Client last name or family name.

    :type: str, max length 50
    """

    fullname = db.Column(db.String(100))
    """
    Client full name.

    Create this field by combining :attr:`firstname` + ' ' + :attr:`lastname`.
    The full name is used for displaying and addressing the client.

    :type: str, max length 100
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

    address = db.Column(db.String(120))
    """
    Client full address.

    Generate by combining :attr:`street`, :attr:`city`, :attr:`state`,
    :attr:`zipcode`, and :attr:`country`.

    :type: str, max length 120
    """

    email = db.Column(db.String(50))
    """
    Client email address.

    :type: str, max length 50
    """

    phone = db.Column(db.String(20))
    """
    Client phone number.

    :type: str, max length 20
    """

    preferred = db.Column(db.SmallInteger)
    """
    Client preferred contact method.

    :type: int, smallint, signed int16
    """

    ringsize = db.Column(db.Float)
    """
    Client ring size.

    Used for ordering an Oura Ring.

    :type: float
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

    def get_medical_record_hash(self):
        """medical record hash generation"""
        name_hash = md5(bytes((self.firstname+self.lastname), 'utf-8')).hexdigest()

        return (self.firstname[0]+self.lastname[0]+str(self.clientid)+name_hash[0:6]).upper()

    def get_attributes(self):
        """return class attributes as list"""
        return  ['address', 'city', 'clientid', 'country', 'dob', 'email', 'emergency_contact', 'emergency_phone', 'firstname','fullname', \
                 'gender','guardianname', 'guardianrole', 'healthcare_contact', 'healthcare_phone', 'lastname',  \
                'middlename', 'phone', 'preferred', 'profession', 'receive_docs', 'ringsize', 'state', 'street','zipcode']

    def to_dict(self):
        """returns all client info in dictionary form"""
        data = {
            'clientid': self.clientid,
            'record_locator_id': self.get_medical_record_hash(),
            'firstname': self.firstname,
            'middlename': self.middlename,
            'lastname': self.lastname,
            'fullname': self.fullname,
            'guardianname': self.guardianname,
            'guardianrole': self.guardianrole,
            'address':self.address,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,
            'country': self.country,
            'email': self.email,
            'phone': self.phone,
            'preferred': self.preferred,
            'ringsize': self.ringsize,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'healthcare_contact': self.healthcare_contact,
            'healthcare_phone': self.healthcare_phone,
            'gender': self.gender,
            'dob': self.dob,
            'profession': self.profession,
            'receive_docs': self.receive_docs
        }
        return data

    def client_info_search_dict(self):
        """returns just the searchable client info (name, email, number)"""
        data = {
            'clientid': self.clientid,
            'record_locator_id': self.get_medical_record_hash(),
            'firstname': self.firstname,
            'lastname': self.lastname,
            'fullname': self.fullname,
            'phone': self.phone,
            'email': self.email
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

    def from_dict(self, data):
        """to be used when a new user is created or a user id edited"""
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])
        if isinstance(self.dob ,str):
            self.dob = datetime.strptime(self.dob, '%Y-%m-%d')

class ClientFacilities(db.Model):
    """ A mapping of client ids to registered facilitiy ids
    """

    __tablename__ = 'ClientFacilities'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    client_id = db.Column(db.ForeignKey('ClientInfo.clientid',ondelete="CASCADE"))
    """
    Foreign key from ClientInfo table

    :type: int, foreign key
    """
    
    facility_id = db.Column(db.ForeignKey('RegisteredFacilities.facility_id',ondelete="CASCADE"))
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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientConsent_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    infectious_disease = db.Column(db.Boolean)
    """
    Indicates whether or not client ever had an infectious disease.

    :type: bool
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

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

    def get_attributes(self):
        """return class attributes as list"""
        return [ 'infectious_disease', 'signdate', 'signature' ]

    def from_dict(self, clientid, data):
        """to be used when a new user is created or a user is edited"""
        setattr(self, 'clientid', clientid) #set clientid of new objects
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        """retuns all data in ClientConsent Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'infectious_disease': self.infectious_disease,
            'signdate': self.signdate,
            'signature': self.signature,
            'revision': self.revision
        }
        return data

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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientRelease_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
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
    Signature date.

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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientPolicies_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

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

    def get_attributes(self):
        """return class attributes as list"""
        return [ 'signdate', 'signature' ]

    def from_dict(self, clientid, data):
        """to be used when a new user is created or a user is edited"""
        setattr(self, 'clientid', clientid) #set clientid of new objects
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        """retuns all data in ClientPolicies Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'signdate': self.signdate,
            'signature': self.signature,
            'revision': self.revision
        }
        return data


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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientColusultContract_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

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

    def get_attributes(self):
        """return class attributes as list"""
        return [ 'signdate', 'signature' ]

    def from_dict(self, clientid, data):
        """to be used when a new user is created or a user is edited"""
        setattr(self, 'clientid', clientid) #set clientid of new objects
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        """retuns all data in ClientConsultConstract Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'signdate': self.signdate,
            'signature': self.signature,
            'revision': self.revision
        }
        return data


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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientSubscriptionContract_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    signdate = db.Column(db.Date)
    """
    Signature date.

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

    def get_attributes(self):
        """return class attributes as list"""
        return [ 'signdate', 'signature' ]

    def from_dict(self, clientid, data):
        """to be used when a new user is created or a user is edited"""
        setattr(self, 'clientid', clientid) #set clientid of new objects
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        """retuns all data in ClientSubscriptionContract Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'signdate': self.signdate,
            'signature': self.signature,
            'revision': self.revision
        }
        return data


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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientIndividualContract_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
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

    def get_attributes(self):
        """return class attributes as list"""
        return [ 'signdate', 'signature', 'data', 'doctor', 'pt', 'drinks']

    def from_dict(self, clientid, data):
        """to be used when a new user is created or a user is edited"""
        setattr(self, 'clientid', clientid) #set clientid of new objects
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        """retuns all data in ClientSubscriptionContract Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'data': self.data,
            'doctor': self.doctor,
            'pt': self.pt,
            'drinks': self.drinks,
            'signdate': self.signdate,
            'signature': self.signature,
            'revision': self.revision
        }
        return data

class RemoteRegistration(db.Model):
    """ At-home client registration parameter

    Stores details to enable clients to register at home securely. This inclues the
    temporary registration url, client login details, and current api token. Each at-home
    client will have one entry in this table. Expired urls will remain for record keeping.

    The primary index of this table is the
    :attr:`clientid` number.
    """

    __tablename__ = 'ClientRemoteRegistration'


    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='remote_registration_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    email = db.Column(db.String(50))
    """
    Client email address.

    :type: str, max length 50
    """

    token = db.Column(db.String(32), index=True, unique=True)
    """
    API authentication token

    :type: str, max length 32, indexed, unique
    """

    token_expiration = db.Column(db.DateTime)
    """
    token expiration date

    :type: datetime
    """

    password = db.Column(db.String(128))
    """
    Hashed password string, as generated by :func:`werkzeug.security.generate_password_hash`.

    :type: str, max length 128
    """

    registration_portal_id = db.Column(db.String(32), index=True, unique=True)
    """
    registration portal endpoint

    :type: str, max length 32, indexed, unique
    """

    registration_portal_expiration = db.Column(db.DateTime)
    """
    token expiration date

    :type: datetime
    """

    def get_temp_registration_endpoint(self, expires_in = 86400):
        """creates a temporary endpoint meant for at-home
           registration
        """
        now = datetime.utcnow()
        self.registration_portal_id = secrets.token_hex(16)
        self.registration_portal_expiration = now + timedelta(seconds=expires_in)

        db.session.add(self)
        db.session.commit()

        return self.registration_portal_id


    def set_password(self):
        """create temporary password, hash it"""
        password = self.email[0:2]+secrets.token_hex(4)
        self.password = password
        return password

    def check_password(self, password):
        return password == self.password

    def get_token(self,expires_in=86400):
        now = datetime.utcnow()
        #returns current token if it is valid
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        #otherwise generate new token, add to session
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self.token

    def revoke_token(self):
        """set token to expired, for logging out/generating new token"""
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.add(self)
        db.session.flush()
        db.session.commit()

    @staticmethod
    def check_token(token):
        """check if token is valid. returns user if so"""
        remote_client = RemoteRegistration.query.filter_by(token=token).first()

        if remote_client is None or remote_client.token_expiration < datetime.utcnow():
            return None
        return remote_client

    @staticmethod
    def check_portal_id(portal_id):
        """check if token is valid. returns user if so"""
        # get most recent instance of the remote client based on registration
        # portal id and index
        remote_client = RemoteRegistration.query.filter_by(
            registration_portal_id=portal_id).order_by(
            RemoteRegistration.idx.desc()).first()

        if remote_client is None or remote_client.registration_portal_expiration < datetime.utcnow():
            return None
        return remote_client

class ClientExternalMR(db.Model):
    """ Client external medical record table

    This table stored medical record ids from external medical institutes. 
    """

    __tablename__ = 'ClientExternalMR'

    __table_args__ = (
        db.UniqueConstraint('clientid', 'med_record_id', 'institute_id'),)

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientExternalMR_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    med_record_id = db.Column(db.String, nullable=False)
    """
    medical record id 
    :type: str
    """

    institute_id = db.Column(db.Integer, db.ForeignKey('MedicalInstitutions.institute_id',name='ClientExternalMR_institute_id_fkey', ondelete="CASCADE"), nullable=False)
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

    release_contract_id = db.Column(db.Integer, db.ForeignKey('ClientRelease.idx',name='ClientReleaseContacts_idx_fkey',ondelete="CASCADE"), nullable=False)
    """
    ID refering back to the signed contract in the ClientRelease table

    :type: int, foreign key to :attr:`ClientRelease.idx`
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='ClientReleaseContacts_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
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

