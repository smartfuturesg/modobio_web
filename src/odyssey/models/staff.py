"""
Database tables staff member information for the Modo Bio Staff application.
All tables in this module are prefixed with ``Staff``.
"""

import base64
from datetime import datetime, timedelta
import os

from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db, whooshee
from odyssey.constants import DB_SERVER_TIME

#@whooshee.register_model('firstname', 'lastname', 'email', 'phone', 'user_id')
class StaffProfile(db.Model):
    """ Staff member profile information table.

    This table stores information regarding Modo Bio
    staff member profiles.
    """
    __tablename__ = 'StaffProfile'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

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

    Stores the history of client removal request by staff members.
    """
    __tablename__ = 'ClientRemovalRequests'
    
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
    
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    Staff member user_id number, foreign key to User.user_id

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the removal request.

    :type: :class:`datetime.datetime`, primary key
    """

class StaffRoles(db.Model):
    """ 
    Stores informaiton on staff role assignments. 

    Roles must be verified either by a manual or automatic internal review process.
    Some roles will be location based where verification is required for each locality
    (state, country etc.)

    Each user_id, role, and locality (state, country) will have a unique entry in this table.
    """
    __tablename__ = 'StaffRoles'
    
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
    
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    Staff member user_id number, foreign key to User.user_id

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    role = db.Column(db.String, nullable=False)
    """
    Name of the role assignment
    Possible roles include:
        - stfappadmin
        - sysadmin
        - clntsvc
        - physthera
        - phystrain
        - datasci
        - doctor
        - nutrition
        - clntsvc_internal
        - physthera_internal
        - phystrain_internal
        - doctor_internal
        - nutrition_internal

    Internal roles are intended for staff members who are part of the internal application development team. 
    
    :type: str
    """

    verified = db.Column(db.Boolean, default=False)
    """
    Weather or not the role entry is verified. Entries to this table will not inherently be 
    verified. 

    :type: bool
    """


