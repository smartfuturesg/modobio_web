"""
Database tables staff member information for the Modo Bio Staff application.
All tables in this module are prefixed with ``Staff``.
"""

import base64
from datetime import datetime, timedelta
import os

from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db, whooshee
from odyssey.utils.constants import DB_SERVER_TIME

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
