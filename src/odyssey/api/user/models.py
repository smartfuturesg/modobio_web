"""
Database tables for the user system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'User'.
"""
import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
import jwt
import random
from sqlalchemy.orm import relation
from werkzeug.security import generate_password_hash

from flask import current_app
from sqlalchemy import text, CheckConstraint

from odyssey import db
from odyssey.utils.constants import ALPHANUMERIC, DB_SERVER_TIME, TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx
from odyssey.api.client.models import ClientInfo
from odyssey.api.staff.models import StaffProfile

class User(db.Model):
    """ 
    Stores details to relating to user account not related to the login system
    """
    __searchable__ = ['modobio_id', 'email', 'phone_number', 'firstname', 'lastname', 'user_id','dob']

    __tablename__ = 'User'

    membersince = db.Column(db.DateTime)
    """
    Member since date, populated when email has been verified

    :type: datetime
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

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    User ID number

    :type: int, primary key, auto-incrementing
    """

    modobio_id = db.Column(db.String)
    """
    User modobio id - serves as a public id for api usage.

    :type: str
    """

    email = db.Column(db.String(75), unique=True)
    """
    Email address.

    The email address is also the login username.

    :type: str, max length 50, non-null, unique
    """

    phone_number = db.Column(db.String(50), unique=False)
    """
    User phone number

    :type: str, max length 50
    """

    firstname = db.Column(db.String(50))
    """
    User first name

    :type: str, max length 50
    """

    middlename = db.Column(db.String(50))
    """
    User first name

    :type: str, max length 50
    """

    lastname = db.Column(db.String(50))
    """
    User first name

    :type: str, max length 50
    """

    biological_sex_male =  db.Column(db.Boolean, server_default='false')
    """
    Client biological sex, true for male, false for female.

    :type: bool
    """

    is_staff = db.Column(db.Boolean, nullable=False, server_default='false')
    """
    Denotes if this user is a staff member. Note: a user can be both a client and a staff member.

    :type: boolean
    """

    was_staff = db.Column(db.Boolean, nullable=False, server_default='false')
    """
    Denotes if this user was ever a staff member. This is important to retain necessary staff info 
    even if a user has deleted their staff account and then later deletes their client account.

    :type: boolean
    """


    staff_profile = db.relationship('StaffProfile', uselist=False, back_populates='user_info')
    """
    One-to-One relationship with StaffProfile

    :type: :class: `StaffProfile` instance
    """

    roles = db.relationship('StaffRoles', uselist=True, foreign_keys='StaffRoles.user_id')
    """
    One-to-Many relationship between User and StaffRoles tables

    :type: :class:`StaffRoles` instance list 
    """

    is_client = db.Column(db.Boolean, nullable=False, server_default='false')
    """
    Denotes if this user is a client. Note: a user can be both a client and a staff member.

    :type: boolean
    """

    client_info = db.relationship('ClientInfo', uselist=False, back_populates='user_info')
    """
    One-to-One relatinoship with ClientInfo

    :type: :class: `ClientInfo` instance
    """

    is_internal = db.Column(db.Boolean, nullable=False, server_default='false')
    """
    Whether or not the user is internal. If True, the user may be able to user features not yet 
    fully released. 

    :type: boolean, non-null 
    """

    deleted = db.Column(db.Boolean, nullable=False, server_default='false')
    """
    Flags if the user has been deleted

    :type: boolean
    """

    email_verified = db.Column(db.Boolean, nullable=False, server_default='false')
    """
    Flags if the user has verified their email

    :type: boolean
    """
    
    dob = db.Column(db.Date)
    """
    User date of birth.

    :type: :class:`datetime.date`
    """

@db.event.listens_for(User, "after_update")
def update_ES_index(mapper, connection, target):
    """
    Listens for any updates to the User table
    """
    from odyssey.utils.search import update_index
    user = {
        'firstname': target.firstname,
        'lastname': target.lastname,
        'phone_number': target.phone_number,
        'email': target.email,
        'modobio_id': target.modobio_id,
        'user_id': target.user_id,
        'is_client': target.is_client,
        'is_staff': target.is_staff,
        'dob': target.dob
    }
    update_index(user, False)

class UserLogin(db.Model):
    """ 
    Stores details to relating to user login and verification.

    The primary index of this table is the
    :attr:`user_id` number.
    """

    __tablename__ = 'UserLogin'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False, unique=True)
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    password = db.Column(db.String(128))
    """
    Hashed password string, as generated by :func:`werkzeug.security.generate_password_hash`.

    :type: str, max length 128
    """

    password_created_at = db.Column(db.DateTime)
    """
    Creation time of the password

    :type: datetime
    """

    password_reset = db.Column(db.Boolean, default=False)
    """
    Used to denote when a user must be forced to change their password. This should be set 
    from a background service based on the user's desired password timeout settings.

    :type: boolean
    """

    # Explicitly setting nullable and default to indicate that None has meaning.
    staff_account_closed = db.Column(db.DateTime, nullable=True, default=None)
    """
    User closed staff portion of the account on this date. A closed account will
    be deleted some time after the close date (initially, 30 days after). If the
    user logs in after closing, but before the account is deleted, this timestamp
    is set to None.

    :type: datetime or None
    """

    staff_account_closed_reason = db.Column(db.String(500))
    """
    Reason why the staff portion of the account was closed.

    :type: str, max length 500
    """

    staff_account_blocked = db.Column(db.Boolean, server_default='f')
    """
    Indicates when the staff portion of the account is blocked.
    See :attr:`staff_account_blocked_reason` for the reason why it was blocked.

    :type: bool
    """

    staff_account_blocked_reason = db.Column(db.String(500))
    """
    Reason why the staff portion of the account was blocked.

    :type: str, max length 500
    """

    # Explicitly setting nullable and default to indicate that None has meaning.
    client_account_closed = db.Column(db.DateTime, nullable=True, default=None)
    """
    User closed client portion of the account on this date. A closed account will
    be deleted some time after the close date (initially, 30 days after). If the
    user logs in after closing, but before the account is deleted, this timestamp
    is set to None.

    :type: datetime or None
    """

    client_account_closed_reason = db.Column(db.String(500))
    """
    Reason why the client portion of the account was closed.

    :type: str, max length 500
    """

    client_account_blocked = db.Column(db.Boolean, server_default='f')
    """
    Indicates when the client portion of the account is blocked.
    See :attr:`client_account_blocked_reason` for the reason why it was blocked.

    :type: bool
    """

    client_account_blocked_reason = db.Column(db.String(500))
    """
    Reason why the client portion of the account was blocked.

    :type: str, max length 500
    """

    last_login = db.Column(db.DateTime)
    """
    **Deprecated 4.12.21 use UserTokensHistory to find last login**

    Time the user last logged in

    :type: datetime
    """

    refresh_token = db.Column(db.String, unique=True)
    """
    **Deprecated 4.12.21 refresh tokens stored in UserTokenHistory**

    API refresh authentication token. Used to generate new access and refresh tokens
    We keep track of the current refresh tokens so we may blacklist tokens as needed.

    :type: str, unique
    """

    def set_password(self, password):
        self.password = generate_password_hash(password)
        self.password_created_at = DB_SERVER_TIME

    @staticmethod
    def generate_token(user_type, user_id, token_type):
        """
        Generate a JWT with the appropriate user type and user_id
        """
        if token_type not in ('access', 'refresh'):
            raise ValueError
        
        secret = current_app.config['SECRET_KEY']
        
        return jwt.encode({'exp': datetime.utcnow()+timedelta(hours =(TOKEN_LIFETIME if token_type == 'access' else REFRESH_TOKEN_LIFETIME)), 
                            'uid': user_id,
                            'utype': user_type,
                            'x-hasura-allowed-roles': [user_type],
                            'x-hasura-user-id': str(user_id),
                            'ttype': token_type
                            }, 
                            secret, 
                            algorithm='HS256')

class UserRemovalRequests(db.Model):
    """ User removal request table.

    Stores the history of user removal request by all Users.
    """
    __tablename__ = 'UserRemovalRequests'
    
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
    
    requester_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    user_id number, foreign key to User.user_id of the User requesting removal

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """


    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    user_id number, foreign key to User.user_id of the User to be removed

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """
    
    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the removal request.

    :type: :class:`datetime.datetime`, primary key
    """
    
    removal_type = db.Column(db.String)
    """
    Type of removal requested. Can be 'client', 'staff', 'or both.

    :type: str
    """

class UserSubscriptions(db.Model):
    """ 
    Stores details to relating to user account not related to the subscription system
    """

    __tablename__ = 'UserSubscriptions'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    table index

    :type: integer, primary key, autoincrementing
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    Id of the user that this subscription belongs to

    :type: int, foreign key('User.user_id')
    """

    is_staff = db.Column(db.Boolean)
    """
    Denotes if this subscription is for a staff member. Distinguishes between 
    subscriptions for users with both account types

    :type: bool
    """

    start_date = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Datetime that this subscription level started

    :type: datetime
    """

    end_date = db.Column(db.DateTime)
    """
    Datetime that this subscription level ended

    :type: datetime
    """

    subscription_status = db.Column(db.String)
    """
    Status of this subscription. Possible values are: unsubscribed, subscribed, free_trial and sponsored

    :type: String
    """

    subscription_type_id = db.Column(db.Integer, db.ForeignKey('LookupSubscriptions.sub_id'))
    """
    Id of this subscription plan. Comes from the LookupSubscriptions table.

    :type: int, foreign key('LookupSubscriptions.sub_id')
    """

    last_checked_date = db.Column(db.DateTime)
    """
    Date the subscription status was last checked with the Apple Store. 
    
    :type: datetime
    """

    apple_original_transaction_id = db.Column(db.String)
    """
    Original transaction id used to track all in-app purchases. This id remains the same for each client purchase.

    https://developer.apple.com/documentation/appstoreserverapi/originaltransactionid

    :type: String
    """

    expire_date = db.Column(db.DateTime)
    """
    Date and time the subscription will expire. If subscription is renewed, there will be a new entry for the 
    subscription renewal.

    :type: datetime
    """

    subscription_type_information = db.relationship("LookupSubscriptions")
    """
    Relationship lookup subscriptions
    """

    
class UserTokensBlacklist(db.Model):
    """ 
    API tokens for either refresh or access which have been revoked either by the 
    user or the API. 

    :attr:`token` 
    """

    __tablename__ = 'UserTokensBlacklist'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    token = db.Column(db.String, index=True, unique=True)
    """
    API token that has been revoked by the user or the API.

    :type: str, unique
    """


class UserPendingEmailVerifications(db.Model):
    """ 
    Holds information about user's who have not yet verified their email.
    """

    __tablename__ = 'UserPendingEmailVerifications'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False, unique = True)
    """
    Id of the user that this pending verification belongs to.

    :type: int, foreign key('User.user_id')
    """

    token = db.Column(db.String)
    """
    JWT token that will verify this user's email when the link is clicked.

    :type: string
    """

    code = db.Column(db.String(4))
    """
    4 digit code that can be used in place of the token in case of problems with the token.

    :type: string
    """

    email = db.Column(db.String(75), unique=True)
    """
    Email address.

    The email address is also the login username.

    :type: str, max length 75, non-null, unique
    """


class UserTokenHistory(db.Model):
    """ 
    Stores details of user token generation events. This includes logging in through basic authorization
    and when users request a new access token using a refresh token 

    The primary index of this table is the
    :attr:`user_id` number.
    """

    __tablename__ = 'UserTokenHistory'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    user_id = db.Column(db.Integer, nullable=True)
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    event = db.Column(db.String)
    """
    Used to specify the token issueance type. Options are
    - 'login'
    - 'refresh'

    :type: str
    """

    refresh_token = db.Column(db.String)
    """
    API refresh authentication token. Used to generate new access and refresh tokens
    We keep track of the current refresh tokens so we may blacklist tokens as needed.

    :type: str, unique
    """

    ua_string = db.Column(db.String)
    """
    Stores contents of user-agent string

    :type: str
    """

class UserResetPasswordRequestHistory(db.Model):
    """
    Stores a history of password reset requests
    """

    __tablename__ = 'UserResetPasswordRequestHistory'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    requested_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when request is submitted

    :type: datetime
    """

    email = db.Column(db.String(75))
    """
    email provided with password reset request

    :type: str, max length 75
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=True)
    """
    user_id connected to email provided if it exists, otherwise blank

    :type: str
    """

    ua_string = db.Column(db.String)
    """
    Stores contents of user-agent string for device submitting request

    :type: str
    """

class UserLegalDocs(db.Model):
    """ 
    Stores details of which legal docs users have seen and signed or attempted to ignore.
    If no entry exists for a given user_id and document id, that user has not yet viewed the document.
    If an entry exists and signed = False, the user has viewed the document but did not sign it.

    The primary index of this table is the
    :attr:`idx` number.
    """

    __tablename__ = 'UserLegalDocs'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Auto incrementing primary key

    :type: int, primary key
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"))
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    doc_id = db.Column(db.Integer, db.ForeignKey('LookupLegalDocs.idx', ondelete="CASCADE"))
    """
    Document ID number, foreigh key to LookupLegalDocs.idx

    :type: int, foreign key
    """

    signed = db.Column(db.Boolean, default=False)
    """
    Denotes if the user has signed this document. If False, the user has viewed the document but no signed.

    :type: boolean
    """

class UserProfilePictures(BaseModelWithIdx):
    """ 
    Stores S3 keys to profile pictures saved in aws s3
    """

    # Either client_user_id OR staff_user_id is used but not both and not neither (XOR).
    __table_args__ = (
        CheckConstraint(
            '(client_user_id IS NULL) != (staff_user_id IS NULL)',
            name='UserProfilePictures_check_user_id'),)

    client_user_id = db.Column(db.Integer, db.ForeignKey('ClientInfo.user_id', ondelete="CASCADE"))
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    client_info = db.relationship('ClientInfo', back_populates='profile_pictures', foreign_keys=[client_user_id])
    """
    Many to one relationship with ClientInfo

    :type: :class:`ClientInfo` instance
    """

    staff_user_id = db.Column(db.Integer, db.ForeignKey('StaffProfile.user_id', ondelete="CASCADE"))
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    staff_profile = db.relationship('StaffProfile', back_populates='profile_pictures', foreign_keys=[staff_user_id])
    """
    Many to one relationship with StaffProfile

    :type: :class:`StaffProfile` instance
    """

    image_path = db.Column(db.String, nullable=False)
    """
    String of image path as it is saved in S3. Required

    :type: str
    """

    width = db.Column(db.Integer)
    """
    Width of image in pixels

    :type: int
    """

    height = db.Column(db.Integer)
    """
    Height of image in pixels

    :type: int
    """
    
    original = db.Column(db.Boolean, server_default='f')
    """
    Boolean determining if the image is the original or not, false by default

    :type: bool
    """

class UserActiveCampaign(BaseModelWithIdx):
    "Stores the data related to Active Campaign"

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"))
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    email = db.Column(db.String)
    """
    User email address saved in Active Campaign 

    :type: string
    """ 
    
    active_campaign_id = db.Column(db.Integer)
    """
    Contact ID from Active Campaign associated with the user

    :type: : int
    """

class UserActiveCampaignTags(BaseModelWithIdx):
    "Stores the tags the user is tagged with on Active Campaign"

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"))
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    tag_id = db.Column(db.Integer, nullable=True)
    """
    User tag association ID returned from Active Campaign

    :type: int
    """

    tag_name = db.Column(db.String)
    """
    Tag name 

    :type: string
    """
