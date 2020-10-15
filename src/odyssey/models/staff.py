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

@whooshee.register_model('firstname','lastname','email','user_id')
class StaffProfile(db.Model):
    """ Staff member profile information table.

    This table stores information regarding Modo Bio
    staff member profiles.
    """
    __tablename__ = 'StaffProfile'

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

    user_id = db.Column((db.Integer, db.ForeignKey('User.user_id',nullable=False))
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    membersince = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Member since date

    The date a staff member was first added to the system

    :type: datetime
    """

    bio = db.Column(db.String)
    """
    staff member profile biography

    :type: string
    """

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
    
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id',nullable=False)
    """
    Staff member user_id number, foreign key to User.user_id

    :type: int, foreign key
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the removal request

    :type: datetime.datetime, primary key
    """