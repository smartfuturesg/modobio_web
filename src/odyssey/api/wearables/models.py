"""
Database tables for the wearable devices section of the Modo Bio API.
All tables in this module are prefixed with 'Wearables'.
"""

from sqlalchemy.dialects.postgresql import ARRAY

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class Wearables(db.Model):
    """ Table that lists which supported wearables a client has. """

    __tablename__ = 'Wearables'

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

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
             'User.user_id',
             ondelete="CASCADE"
        ),
        nullable=False,
        unique=True)
    """
    User ID number.

    :type: int, unique, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    has_oura = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client has an Oura Ring wearable.

    :type: bool, default = False
    """

    registered_oura = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client granted Modo Bio access to Oura Cloud.

    :type: bool, default = False
    """

    has_fitbit = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client has an Fitbit wearable.

    :type: bool, default = False
    """

    registered_fitbit = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client granted Modo Bio access to Fitbit data.

    :type: bool, default = False
    """

    has_freestyle = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client has an FreeStyle Libre continuous glucose monitoring (CGM) wearable.

    :type: bool, default = False
    """

    registered_freestyle = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client has activated the FreeStyle Libre continuous glucose monitoring (CGM) wearable.

    :type: bool, default = False
    """

    has_applewatch = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client has an Apple Watch wearable.

    :type: bool, default = False
    """

    registered_applewatch = db.Column(db.Boolean, default=False, nullable=False)
    """
    Client granted Modo Bio access to Apple Watch data.

    :type: bool, default = False
    """

    oura = db.relationship('WearablesOura', uselist=False, back_populates='wearable')
    """
    WearablesOura instance holding Oura specific data.

    :type: :class:`WearablesOura` instance
    """

    fitbit = db.relationship('WearablesFitbit', uselist=False, back_populates='wearable')
    """
    WearablesFitbit instance holding Fitbit specific data.

    :type: :class:`WearablesFitbit` instance
    """

    freestyle = db.relationship('WearablesFreeStyle', uselist=False, back_populates='wearable')
    """
    WearablesFreeStyle instance holding FreeStyle specific data.

    :type: :class:`WearablesFreeStyle` instance
    """


class WearablesOura(db.Model):
    """ Oura Ring specific information. """

    __tablename__ = 'WearablesOura'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
             'User.user_id',
             ondelete="CASCADE"
        ),
        nullable=False,
        unique=True)
    """
    Client ID number.

    :type: int, unique, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
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

    oauth_state = db.Column(db.String(512))
    """
    State token for OAuth2 exchange with Oura Cloud.

    This token is a state parameter, it must not change in between the various phases
    of OAuth2 authorization. It is stored temporarily in the database, but has no meaning
    after the OAuth2 process is completed. If a token exists in this column, it is a sign
    that the grant-to-access token exchange did not complete successfully.

    :type: str, max length 512
    """

    access_token = db.Column(db.String(512))
    """
    OAuth2 access token to authorize Oura Cloud access.

    :type: str, max length 512
    """

    refresh_token = db.Column(db.String(512))
    """
    OAuth2 refresh token to obtain a new :attr:`access_token` after it expires.

    :type: str, max length 512
    """

    token_expires = db.Column(db.DateTime)
    """
    Date and time of :attr:`access_token` expiry.

    :type: :class:`datetime.datetime`
    """

    last_scrape = db.Column(db.DateTime)
    """
    Date and time of last access to Oura Cloud.

    :type: :class:`datetime.datetime`
    """

    wearable_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'Wearables.idx',
            ondelete='CASCADE'
        ),
        nullable=False,
        unique=True)
    """
    Wearable index this WearablesOura instance is linked to.

    :type: int, unique, foreign key to :attr:`Wearables.idx`
    """

    wearable = db.relationship('Wearables', uselist=False, back_populates='oura')
    """
    Wearable instance this WearablesOura instance is linked to.

    :type: :class:`Wearables`
    """


class WearablesFitbit(db.Model):
    """ Fitbit specific information. """

    __tablename__ = 'WearablesFitbit'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
             'User.user_id',
             ondelete="CASCADE"
        ),
        nullable=False,
        unique=True)
    """
    Client ID number.

    :type: int, unique, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    created_at = db.Column(db.DateTime, server_default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, server_default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    oauth_state = db.Column(db.String(512))
    """
    State token for OAuth2 exchange with Fitbit servers.

    This token is a state parameter, it must not change in between the various phases
    of OAuth2 authorization. It is stored temporarily in the database, but has no meaning
    after the OAuth2 process is completed. If a token exists in this column, it is a sign
    that the grant-to-access token exchange did not complete successfully.

    :type: str, max length 512
    """

    access_token = db.Column(db.String(1048))
    """
    OAuth2 access token to authorize Fitbit access. Fitbit uses JWT for access token, which
    may be up to 1024 bytes in size.
    https://dev.fitbit.com/build/reference/web-api/oauth2/#fitbit-api-notes

    :type: str, max length 1024
    """

    refresh_token = db.Column(db.String(512))
    """
    OAuth2 refresh token to obtain a new :attr:`access_token` after it expires.

    :type: str, max length 512
    """

    token_expires = db.Column(db.DateTime)
    """
    Date and time of :attr:`access_token` expiry.

    :type: :class:`datetime.datetime`
    """

    last_scrape = db.Column(db.DateTime)
    """
    Date and time of last access to Fitbit account.

    :type: :class:`datetime.datetime`
    """

    wearable_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'Wearables.idx',
            ondelete='CASCADE'
        ),
        nullable=False,
        unique=True)
    """
    Wearable index this WearablesFitbit instance is linked to.

    :type: int, unique, foreign key to :attr:`Wearables.idx`
    """

    wearable = db.relationship('Wearables', uselist=False, back_populates='fitbit')
    """
    Wearable instance this WearablesFitbit instance is linked to.

    :type: :class:`Wearables`
    """


class WearablesFreeStyle(db.Model):
    """ FreeStyle Libre continuous glucose monitoring wearable specific information. """

    __tablename__ = 'WearablesFreeStyle'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
             'User.user_id',
             ondelete="CASCADE"
        ),
        nullable=False,
        unique=True)
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

    timestamps = db.Column(ARRAY(db.DateTime, dimensions=1))
    """
    Timestamps for the glucose data.

    :type: list(datetime.datatime)
    """

    glucose = db.Column(ARRAY(db.Float, dimensions=1))
    """
    Glucose data from the GCM.

    :type: list(float)
    """

    activation_timestamp = db.Column(db.DateTime)
    """
    Timestamp when last CGM was activated.

    On the CGM device, the time is stored as minutes since activation. It must
    be converted to a timestamp before it can be added to the timestamps array.
    This timestamp can be used to calculate the timestamp for each data point.

    :type: :class:`datetime.datetime`
    """

    wearable_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'Wearables.idx',
            ondelete='CASCADE'
        ),
        nullable=False,
        unique=True)
    """
    Wearable index this WearablesFreeStyle instance is linked to.

    :type: int, unique, foreign key to :attr:`Wearables.idx`
    """

    wearable = db.relationship('Wearables', uselist=False, back_populates='freestyle')
    """
    Wearable instance this WearablesFreeStyle instance is linked to.

    :type: :class:`Wearables`
    """
