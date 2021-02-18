"""
Database tables for the user system portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'User'.
"""
import enum
import base64
from datetime import datetime, timedelta
import jwt
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app

from odyssey import db
from odyssey.utils.constants import ALPHANUMERIC, DB_SERVER_TIME, TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME

class TelehealthQueueClientPool(db.Model):
    """ 
    Holds all of the clients in a pool for their appointments. 
    This is used for BEFORE they are accepted and see their medical professional.
    """

    __tablename__ = 'TelehealthQueueClientPool'

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
    Id of the user that this notification belongs to

    :type: int, foreign key('User.user_id')
    """

    profession_type = db.Column(db.String)
    """
    TODO: Change this to a relationship with the type of professional ID
    Professional type is used for what type of professional the client wants to meet with

    :type: str
    """

    target_date = db.Column(db.DateTime)
    """
    target date is the date that the client wants for their appointment

    :type: datetime
    """

    priority = db.Column(db.Boolean)
    """
    priority is a flag most likely set by the system admin, default is false.

    :type: bool
    """

