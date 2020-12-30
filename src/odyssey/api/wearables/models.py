"""
Database tables for the wearable devices section of the Modo Bio Staff application.
All tables in this module are prefixed with 'Wearables'.

The models in this file are shared between the Odyssey and the Wearables programs.
They describe tables in the ``modobio`` database.
"""

import sys

# If the Flask module is imported, assume we are running in a flask app,
# and therefore we are part of Odyssey.
if 'flask' in sys.modules:
    from odyssey import db
    _Base = db.Model
else:
    # In the Wearables program, Alembic should not try to update these models
    # in the database. We separate it by giving these models a different base
    # from the rest of the Wearables program.
    from sqlalchemy.ext.declarative import declarative_base
    _Base = declarative_base()

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY

from odyssey.utils.constants import DB_SERVER_TIME

class LookUpActivityTrackers(db.Model):
    """ Look up table for activity trackers and their capabilities. """

    __tablename__ = 'LookUpActivityTrackers'

    idx = Column(Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    brand = db.Column(db.String)
    """
    activity tracker brand name

    :type: str
    """

    series = db.Column(db.String)
    """
    activity tracker series

    :type: str
    """

    model = db.Column(db.String)
    """
    activity tracker model

    :type: str
    """

    ecg_metric_1 = db.Column(db.Boolean)
    """
    2-lead ECG Metric 1
    Text

    :type: bool
    """

    ecg_metric_2 = db.Column(db.Boolean)
    """
    2-lead ECG Metric 2
    Beats Per Minute

    :type: bool
    """

    sp_o2_spot_check = db.Column(db.Boolean)
    """
    % Oxygenation (no decimals)

    :type: bool
    """

    sp_o2_nighttime_avg = db.Column(db.Boolean)
    """
    % Oxygenation (no decimals)

    :type: bool
    """

    sleep_total = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    deep_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    rem_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    quality_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    light_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    awake = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    sleep_latency = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    bedtime_consistency = db.Column(db.Boolean)
    """
    + or - Time HH:MM

    :type: bool
    """                            

    wake_consistency = db.Column(db.Boolean)
    """
    + or - Time HH:MM

    :type: bool
    """

    rhr_avg = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """    

    rhr_lowest = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """    
    
    hr_walking = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """     

    hr_24hr_avg = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """ 

    hrv_avg = db.Column(db.Boolean)
    """
    milliseconds (ms)

    :type: bool
    """    

    hrv_highest = db.Column(db.Boolean)
    """
    milliseconds (ms)

    :type: bool
    """

    respiratory_rate = db.Column(db.Boolean)
    """
    per minute

    :type: bool
    """

    body_temperature = db.Column(db.Boolean)
    """
    + or - degrees farenheit

    :type: bool
    """

    steps = db.Column(db.Boolean)
    """
    number
    
    :type: bool
    """

    total_calories = db.Column(db.Boolean)
    """
    calories (kcal)

    :type: bool
    """

    active_calories = db.Column(db.Boolean)
    """
    calories

    :type: bool
    """
    
    walking_equivalency = db.Column(db.Boolean)
    """
    number miles

    :type: bool
    """

    inactivity = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

class Wearables(_Base):
    """ Table that lists which supported wearables a client has. """

    __tablename__ = 'Wearables'

    idx = Column(Integer, primary_key=True, autoincrement=True)
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

    user_id = Column(
        Integer,
        ForeignKey(
             'User.user_id',
             ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    User ID number.

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    has_oura = Column(Boolean, default=False, nullable=False)
    """
    Client has an Oura Ring wearable.

    :type: bool, default = False
    """

    registered_oura = Column(Boolean, default=False, nullable=False)
    """
    Client granted Modo Bio access to Oura Cloud.

    :type: bool, default = False
    """

    has_freestyle = Column(Boolean, default=False, nullable=False)
    """
    Client has an FreeStyle Libre continuous glucose monitoring (CGM) wearable.

    :type: bool, default = False
    """


class WearablesOura(_Base):
    """ Oura Ring specific information. """

    __tablename__ = 'WearablesOura'

    idx = Column(Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    user_id = Column(
        Integer,
        ForeignKey(
             'User.user_id',
             ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    Client ID number.

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

    oauth_state = Column(String(50))
    """
    State token for OAuth2 exchange with Oura Cloud.

    This token is a state parameter, it must not change in between the various phases
    of OAuth2 authorization. It is stored temporarily in the database, but has no meaning
    after the OAuth2 process is completed. If a token exists in this column, it is a sign
    that the grant-to-access token exchange did not complete successfully.

    :type: str, max length 50
    """

    access_token = Column(String(50))
    """
    OAuth2 access token to authorize Oura Cloud access.

    :type: str, max length 50
    """

    refresh_token = Column(String(50))
    """
    OAuth2 refresh token to obtain a new :attr:`access_token` after it expires.

    :type: str, max length 50
    """

    token_expires = Column(DateTime)
    """
    Date and time of :attr:`access_token` expiry.

    :type: :class:`datetime.datetime`
    """

    last_scrape = Column(DateTime)
    """
    Date and time of last access to Oura Cloud.

    :type: :class:`datetime.datetime`
    """


class WearablesFreeStyle(_Base):
    """ FreeStyle Libre continuous glucose monitoring wearable specific information. """

    __tablename__ = 'WearablesFreeStyle'

    idx = Column(Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    user_id = Column(
        Integer,
        ForeignKey(
             'User.user_id',
             ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    Client ID number.

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

    timestamps = Column(ARRAY(DateTime, dimensions=1))
    """
    Timestamps for the glucose data.

    :type: list(datetime.datatime)
    """

    glucose = Column(ARRAY(Float, dimensions=1))
    """
    Glucose data from the GCM.

    :type: list(float)
    """

    activation_timestamp = Column(DateTime)
    """
    Timestamp when last CGM was activated.

    On the CGM device, the time is stored as minutes since activation. It must
    be converted to a timestamp before it can be added to the timestamps array.
    This timestamp can be used to calculate the timestamp for each data point.

    :type: :class:`datetime.datetime`
    """
