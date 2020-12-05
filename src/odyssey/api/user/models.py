"""
Database tables for the user system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'User'.
"""
import base64
from datetime import datetime, timedelta
import jwt
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app

from odyssey import db
from odyssey.utils.constants import ALPHANUMERIC, DB_SERVER_TIME, TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME

#@whooshee.register_model('firstname', 'lastname', 'email', 'phone', 'user_id')
class User(db.Model):
    """ 
    Stores details to relating to user account not related to the login system
    """

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

    connection.execute(statement)

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

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
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
    Time the user last logged in

    :type: datetime
    """

    #todo - remove token after jwt integration
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

    def set_password(self, password):
        self.password = generate_password_hash(password)
        self.password_created_at = DB_SERVER_TIME

    @staticmethod
    def generate_token(user_type, user_id, token_type):
        """
        Generate a JWT with the appropriate user type and user_id
        """
        secret = current_app.config['SECRET_KEY']
        
        return jwt.encode({'exp': datetime.utcnow()+timedelta(hours =(TOKEN_LIFETIME if token_type == 'access' else REFRESH_TOKEN_LIFETIME)), 
                            'uid': user_id,
                            'utype': user_type}, 
                            secret, 
                            algorithm='HS256').decode("utf-8")

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
    
    requester_email = db.Column(db.String, nullable=False)
    """
    user_id number, foreign key to User.user_id of the User requesting removal

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    #requester_user_id = db.Column(db.)

    deleting_email = db.Column(db.String, nullable=False)
    """
    user_id number, foreign key to User.user_id of the User to be removed

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """
    
    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the removal request.

    :type: :class:`datetime.datetime`, primary key
    """
