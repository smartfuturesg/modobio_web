"""
Database tables staff member information for the Modo Bio Staff application.
All tables in this module are prefixed with ``Staff``.
"""

import base64
from datetime import datetime, timedelta
import os

from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

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

class StaffRecentClients(db.Model):
    """this table stores the last 10 clients that a staff member has loaded"""

    __tablename__ = 'StaffRecentClients'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    User_id of the staff member that loaded the client

    :type: int, foreign key
    """

    client_user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    User_id of the client that was loaded

    :type: int, foreign key
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp denoting when the staff member last loaded the client

    :type: datetime
    """

class StaffRoles(db.Model):
    """ Stores informaiton on staff role assignments. 

    Roles must be verified either by a manual or automatic internal review process.
    Some roles will be location based where verification is required for each locality
    (state, country etc.). 
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

    -staff_admin
    -system_admin
    -client_services
    -physical_therapist
    -trainer
    -data_science
    -doctor
    -nutrition
    
    :type: str
    """

    verified = db.Column(db.Boolean, default=False)
    """
    Weather or not the role entry is verified. Entries to this table will not inherently be 
    verified. 

    :type: bool
    """


class StaffOperationalTerritories(db.Model):
    """ 
    Locations where staff members operate. Each entry is tied to a role in the StaffRoles table. 
    Depending on the profession, the role-territory paid must be verified with an active identification number
    or some other internal process. Verifications will be stored in another table. 

    """
    __tablename__ = 'StaffOperationalTerritories'
    
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

    operational_territory_id = db.Column(db.Integer, db.ForeignKey('LookupTerritoriesofOperation.idx'))
    """
    Operational subterritory from the operational territories lookup table.

    There will be an entry in this table for each role-operational_territory pair. For some professions, we will
    store verification IDs which may differ by sub_territory (e.g. medical doctors must have a different license to practice
    in each state).

    :type: int, foreign key to :attr:`LookupTerritoriesofOperation.idx <odyssey.models.lookup.LookupTerritoriesofOperation.idx>`
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    Staff member user_id number, foreign key to User.user_id

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    role_id = db.Column(db.Integer, db.ForeignKey('StaffRoles.idx', ondelete="CASCADE"), nullable=False)
    """
    Role from the StaffRoles table. 

    :type: int, foreign key to :attr:`StaffRoles.idx <odyssey.models.staff.StaffRoles.idx>`
    """

class StaffCalendarEvents(db.Model):
    """ 
    Model for events to be saved to the professional's calendar 

    """
    __tablename__ = 'StaffCalendarEvents'
    
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
    Staff member user_id number, foreign key to User.user_id.

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    start_date = db.Column(db.Date, nullable=False)
    """
    If recurring, this is the recurrence start date,
    if not, this is the event start date

    :type: :class:`datetime.date`
    """

    end_date = db.Column(db.Date, nullable=True)
    """
    If event is recurring, this is the recurrence end date,
    if not, this is the event end date

    :type: :class:`datetime.date`
    """

    start_time = db.Column(db.Time, nullable=False)
    """
    Event start time

    :type: :class:'datetime.time'
    """

    end_time = db.Column(db.Time, nullable=False)
    """
    Event end time

    :type: :class:'datetime.time'
    """

    timezone = db.Column(db.String, nullable=False)
    """
    Local time zone name, saved at event creation

    :type: str
    """

    duration = db.Column(db.Interval, nullable=True)
    """
    Event duration, only important for recurring events

    :type: datetime.timedelta
    """

    all_day = db.Column(db.Boolean, nullable=False)
    """
    Flag if event lasts all day or not

    :type: bool
    """

    recurring = db.Column(db.Boolean, nullable=False)
    """
    Flag to determine if this event is recurring

    :type: bool
    """

    recurrence_type = db.Column(db.String, nullable=True)
    """
    Type of recurrence for the event. Must be one of RECURRENCE_TYPE = ('Daily', 'Weekly', 'Monthly', 'Yearly')

    :type: str
    """

    location = db.Column(db.String(100), nullable=True)
    """
    Event's location
    
    :type: str
    """

    description = db.Column(db.Text, nullable=True)
    """
    Event's description

    :type: str
    """

    availability_status = db.Column(db.String, nullable=False)
    """
    Professional's availabilit status through the event
    Currently, only options are in constants.py -> EVENT_AVAILABILITY = ('Busy', 'Available')

    :type: str
    """

