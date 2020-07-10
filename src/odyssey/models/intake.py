"""
Database tables for the client intake portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Client'.
"""
import base64
import os
import pytz
import random

from datetime import datetime, timedelta
from hashlib import md5
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db

phx_tz = pytz.timezone('America/Phoenix')

class ClientInfo(db.Model):
    """ Client information table

    This table stores general information of a client. The information is taken
    only once, during the initial consult. The primary index of this table is the
    :attr:`clientid` number. Many other tables in this database refer to the
    :attr:`clientid` number, so a new client **MUST** be added to this table first,
    in order to generate the :attr:`clientid` number.
    """

    __tablename__ = 'ClientInfo'

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



class ClientConsent(db.Model):
    """ Client consent form table

    This table stores the signature and related information of the consent form.
    """

    __tablename__ = 'ClientConsent'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
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

    See Also
    --------
    :const:`odyssey.constants.DOCTYPE_DOCREV_MAP`
    """

    url = db.Column(db.String(200))
    """
    URL where signed document is stored as a PDF file.

    :type: str, max length 100
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
            'signature': self.signature
        }
        return data

class ClientRelease(db.Model):
    """ Client release of information table

    This table stores the signature and related information of the
    release of information form.
    """

    __tablename__ = 'ClientRelease'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    release_by_other = db.Column(db.String(1024))
    """
    Describes who else can release protected health information.

    :type: str, max length 1024
    """

    release_to_other = db.Column(db.String(1024))
    """
    Describes to whom else protected health information can be released.

    :type: str, max length 1024
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

    See Also
    --------
    :const:`odyssey.constants.DOCTYPE_DOCREV_MAP`
    """

    url = db.Column(db.String(200))
    """
    URL where signed document is stored as a PDF file.

    :type: str, max length 100
    """

    def get_attributes(self):
        """return class attributes as list"""
        return [ 'release_by_other','release_to_other', 'release_of_all', 'release_of_other', 'release_date_to',
            'release_date_from', 'release_purpose', 'signdate', 'signature' ]

    def from_dict(self, clientid, data):
        """to be used when a new user is created or a user is edited"""
        setattr(self, 'clientid', clientid) #set clientid of new objects
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        """retuns all data in ClientRelease Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'release_by_other': self.release_by_other,
            'release_to_other': self.release_to_other,
            'release_of_all': self.release_of_all,
            'release_of_other': self.release_of_other,
            'release_date_from': self.release_date_from,
            'release_date_to': self.release_date_to,
            'release_purpose': self.release_purpose,
            'signdate': self.signdate,
            'signature': self.signature
        }
        return data


class ClientPolicies(db.Model):
    """ Client policies table

    This table stores the signature and related information of the
    Modo Bio policies form.
    """

    __tablename__ = 'ClientPolicies'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
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

    See Also
    --------
    :const:`odyssey.constants.DOCTYPE_DOCREV_MAP`
    """

    url = db.Column(db.String(200))
    """
    URL where signed document is stored as a PDF file.

    :type: str, max length 100
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
            'signature': self.signature
        }
        return data


class ClientConsultContract(db.Model):
    """ Client initial consultation contract table

    This table stores the signature and related information for the
    initial consultation contract.
    """

    __tablename__ = 'ClientConsultContract'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
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

    See Also
    --------
    :const:`odyssey.constants.DOCTYPE_DOCREV_MAP`
    """

    url = db.Column(db.String(200))
    """
    URL where signed document is stored as a PDF file.

    :type: str, max length 100
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
            'signature': self.signature
        }
        return data


class ClientSubscriptionContract(db.Model):
    """ Client subscription contract table

    This table stores the signature and related information for the
    subscription contract.
    """

    __tablename__ = 'ClientSubscriptionContract'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
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

    See Also
    --------
    :const:`odyssey.constants.DOCTYPE_DOCREV_MAP`
    """

    url = db.Column(db.String(200))
    """
    URL where signed document is stored as a PDF file.

    :type: str, max length 100
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
            'signature': self.signature
        }
        return data


class ClientIndividualContract(db.Model):

    __tablename__ = 'ClientIndividualContract'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
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

    See Also
    --------
    :const:`odyssey.constants.DOCTYPE_DOCREV_MAP`
    """

    url = db.Column(db.String(200))
    """
    URL where signed document is stored as a PDF file.

    :type: str, max length 100
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
            'signature': self.signature
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

    __tablename__ = 'remote_registration'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
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

    def from_dict(self,  data):
        """to be used when a new user is created or a user id edited"""
        for field in ['clientid', 'email']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        """returns all client info in dictionary form"""
        #leaving this heer ein case we need to return this with a local timezone
        # portal_expr_time = phx_tz.localize(self.registration_portal_expiration) + phx_tz.localize(self.registration_portal_expiration).utcoffset()
        data = {
            'clientid': self.clientid,
            'email': self.email,
            'registration_portal_id': self.registration_portal_id,
            'registration_portal_expiration': self.registration_portal_expiration
        }
        return data

    def get_temp_registration_endpoint(self, expires_in = 86400):
        """creates a temporary endpoint meant for at-home
           registration
        """
        now = datetime.utcnow()
        self.registration_portal_id = md5(bytes(self.email+now.strftime("%Y-%m-%d %H:%M:%S"), 'utf-8')).hexdigest()
        self.registration_portal_expiration = now + timedelta(seconds=expires_in)

        db.session.add(self)
        db.session.flush()
        db.session.commit()

        return self.registration_portal_id


    def set_password(self, firstname, lastname):
        """create temporary password, hash it"""
        name_hash = md5(bytes((str(random.randrange(999,99999,1))), 'utf-8')).hexdigest()
        password = firstname[0:2]+lastname[0:2]+name_hash[0:5]
        self.password = generate_password_hash(password)
        return password

    def check_password(self, password):
        return check_password_hash(self.password, password)

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
        remote_client = RemoteRegistration.query.filter_by(registration_portal_id=portal_id).first()

        if remote_client is None or remote_client.registration_portal_expiration < datetime.utcnow():
            return None
        return remote_client
