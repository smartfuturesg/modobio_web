"""
General database tables for the operation of the Modo Bio Staff application.
There is no specific table name prefix for the tables in this module.
"""
import base64
from datetime import datetime, timedelta
import os

from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db, whooshee
from odyssey.constants import DB_SERVER_TIME

@whooshee.register_model('firstname','lastname','email','staffid')
class Staff(db.Model):
    """ Staff member information table.

    This table stores basic login information regarding Modo Bio
    staff members.
    """
    __tablename__ = 'Staff'

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

    access_roles = db.Column(db.ARRAY(db.String), nullable=False, server_default="{'clntsvc'}")
    """
    Indicates the content access role of the staff member.
    roles include: stfappadmin, clntsvc, physthera, phystrain, datasci, doctor, docext, nutrition

    :type: str, default = clntsvc
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

    def get_admin_role(self):
        """check if this staff member is authorized to create new staff members"""
        if self.is_system_admin:
            return 'sys_admin'
        elif self.is_admin:
            return 'staff_admin'
        else:
            return None #not an admin

class ClientRemovalRequests(db.Model):
    """ Client removal request table.

    Stores the history if client removal request by staff members
    """
    __tablename__ = 'ClientRemovalRequests'
    
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
    
    staffid = db.Column(db.Integer, 
                         db.ForeignKey('Staff.staffid',
                            name='ClientRemovalRequests_staffid_fkey'), 
                        nullable=False)
    """
    Staff member ID number

    :type: int, primary key, autoincrement
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the removal request

    :type: datetime.datetime, primary key
    """