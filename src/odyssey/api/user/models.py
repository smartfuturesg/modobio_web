"""
Database tables for the user system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'User'.
"""
from datetime import datetime, timedelta
import jwt
import random
from werkzeug.security import generate_password_hash

from flask import current_app
from sqlalchemy import text

from odyssey import db
from odyssey.utils.constants import ALPHANUMERIC, DB_SERVER_TIME, TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME, EMAIL_TOKEN_LIFETIME

class User(db.Model):
    """ 
    Stores details to relating to user account not related to the login system
    """
    __searchable__ = ['modobio_id', 'email', 'phone_number', 'firstname', 'lastname', 'user_id']

    __tablename__ = 'User'

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

    email = db.Column(db.String(50), unique=True)
    """
    Email address.

    The email address is also the login username.

    :type: str, max length 50, non-null, unique
    """

    phone_number = db.Column(db.String(50), unique=True)
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

    biological_sex_male =  db.Column(db.Boolean)
    """
    Client biological sex, true for male, false for female.

    :type: bool
    """

    is_staff = db.Column(db.Boolean, nullable=False)
    """
    Denotes if this user is a staff member. Note: a user can be both a client and a staff member.

    :type: boolean
    """

    is_client = db.Column(db.Boolean, nullable=False)
    """
    Denotes if this user is a client. Note: a user can be both a client and a staff member.

    :type: boolean
    """

    is_internal = db.Column(db.Boolean, nullable=False, default=False)
    """
    Whether or not the user is internal. If True, the user may be able to user features not yet 
    fully released. 

    :type: boolean, non-null 
    """

    deleted = db.Column(db.Boolean, nullable=True, default = False)
    """
    Flags if the user has been deleted

    :type: boolean
    """

    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    """
    Flags if the user has verified their email

    :type: boolean
    """

    @staticmethod
    def generate_modobio_id(firstname: str, lastname: str, user_id: int) -> str:
        """ Generate the user's mdobio_id.

        The modo bio identifier is used as a public user id, it
        can also be exported to other healthcare providers (clients only).
        It is made up of the firstname and lastname initials and 10 random alphanumeric
        characters.

        Parameters
        ----------
        firstname : str
            Client first name.

        lastname : str
            Client last name.

        user_id : int
            User ID number.

        Returns
        -------
        str
            Medical record ID
        """
        random.seed(user_id)
        rli_hash = "".join([random.choice(ALPHANUMERIC) for i in range(10)])
        return (firstname[0] + lastname[0] + rli_hash).upper()

@db.event.listens_for(User, "after_insert")
def add_modobio_id(mapper, connection, target):
    """
    Listens for new entries into the User table and 
    automatically assigns a modibio_id to new users.

    Parameters
    ----------
    mapper : ???
        What does this do? Not used.

    connection : :class:`sqlalchemy.engine.Connection`
        Connection to the database engine.

    target : :class:`sqlalchemy.schema.Table`
        Target SQLAlchemy table, fixed to :class:`User` by decorator.
    """
    mb_id = User().generate_modobio_id(
            firstname = target.firstname, 
            lastname = target.lastname, 
            user_id = target.user_id)

    statement = f"""UPDATE public."User" 
                set modobio_id = '{mb_id}'
                where user_id = {target.user_id};"""

    connection.execute(text(statement))

    from odyssey.utils.search import update_index
    user = {
        'firstname': target.firstname,
        'lastname': target.lastname,
        'phone_number': target.phone_number,
        'email': target.email,
        'modobio_id': mb_id,
        'user_id': target.user_id,
        'is_client': target.is_client,
        'is_staff': target.is_staff
    }
    update_index(user, True)


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
        'is_staff': target.is_staff
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

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
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

    @staticmethod
    def generate_token(user_id):
        """
        Generate a JWT with the appropriate user type and user_id
        """
        
        secret = current_app.config['SECRET_KEY']
        
        return jwt.encode({'exp': datetime.utcnow()+timedelta(hours=EMAIL_TOKEN_LIFETIME),
                            'uid': user_id,
                            'ttype': 'email_verification'
                            }, 
                            secret, 
                            algorithm='HS256')

    @staticmethod
    def generate_code():
        """
        Generate a 4 digit code
        """

        return str(random.randrange(1000, 9999))

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