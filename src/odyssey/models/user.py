"""
Database tables for the user system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'User'.
"""
import base64
import os

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db
from odyssey.constants import DB_SERVER_TIME

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

    modobio_id = db.Column(db.Integer)
    """
    User modobio id - serves as a public id for api usage.

    :type: int
    """

    email = db.Column(db.String(50))
    """
    User email address.

    :type: str, max length 50
    """

    phone_number = db.Column(db.String(50))
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
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
        user = User.query.filter_by(token=token).first()

        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user