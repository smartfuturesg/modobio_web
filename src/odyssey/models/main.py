"""
General database tables for the operation of the Modo Bio Staff application.
There is no specific table name prefix for the tables in this module.
"""
import base64
from datetime import datetime, timedelta
import os

from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db

class Staff(db.Model):
    """ Staff member information table.

    This table stores basic login information regarding Modo Bio
    staff members.
    """
    __tablename__ = 'Staff'

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

    staffid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Staff member ID number

    :type: int, primary key, autoincrement
    """

    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    """
    Indicates whether staff member is an administrator, i.e. has the
    ability to add/delete members to the Staff table.

    :type: bool, default = False
    """

    is_system_admin = db.Column(db.Boolean, nullable=False, default=False)
    """
    Indicates whether staff member is a system administrator. There should be very few of these
    roles given out. 

    :type: bool, default = False
    """

    access_role = db.Column(db.String, nullable=False, default='cs')
    """
    Indicates the content access role of the staff member.
    roles include: client services (cs), pt, doctor, data 

    :type: str, default = cs
    """

    email = db.Column(db.String(50), nullable=False, unique=True)
    """
    Email address of staff member, used as login.

    :type: str, max length 50, non-null, unique
    """

    firstname = db.Column(db.String(50), nullable=False)
    """
    First name of staff member.

    :type: str, max length 50, non-null
    """

    lastname = db.Column(db.String(50), nullable=False)
    """
    Last name of staff member.

    :type: str, max length 50, non-null
    """

    fullname = db.Column(db.String(100))
    """
    Full name  of staff member. Combination of :attr:`firstname` + :attr:`lastname`.

    :type: str, max length 100
    """

    password = db.Column(db.String(128))
    """
    Hashed password string, as generated by :func:`werkzeug.security.generate_password_hash`.

    :type: str, max length 128
    """



    def to_dict(self):
        """returns all Staff info in dictionary form (except password and token)"""
        data = {
            'staff_id': self.staffid,
            'first_name': self.firstname,
            'last_name': self.lastname,
            'full_name': self.fullname,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_system_admin': self.is_system_admin,
            'access_role': self.access_role
        }

        return data

    def from_dict(self, data, new_staff=False):
        for field in ['firstname', 'lastname', 'fullname', 'email', 'is_admin', 'is_system_admin', 'access_role']:
            if field in data:
                setattr(self, field, data[field])

        if new_staff and 'password' in data:
            self.set_password(data['password'])

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_token(self,expires_in=360000):
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
        staff_member = Staff.query.filter_by(token=token).first()

        if staff_member is None or staff_member.token_expiration < datetime.utcnow():
            return None
        return staff_member

    def get_admin_role(self):
        """check if this staff member is authorizewd to create new staff members"""
        if self.is_system_admin:
            return 'sys_admin'
        elif self.is_admin:
            return 'staff_admin'
        else:
            return None #not an admin

