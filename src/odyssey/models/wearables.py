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

class Wearables(_Base):
    """ Table that lists which supported wearables a client has. """

    __tablename__ = 'Wearables'

    idx = Column(Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = Column(
        Integer,
        ForeignKey(
             'ClientInfo.clientid',
             ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid`
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

    clientid = Column(
        Integer,
        ForeignKey(
             'ClientInfo.clientid',
             ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid`
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

    grant_token = Column(String(50))
    """
    OAuth2 access grant token to authorize Oura Cloud access.

    This token is a one-time access grant token, issued immediately after the client
    clicks 'Accept' on the Oura Ring website. It is exchanged for :attr:`access_token`,
    but since that exchange can fail, the grant token is temporarily stored. If a token
    exists in this column, it is a sign that the grant-to-access token exchange did
    not complete successfully.

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

    clientid = Column(
        Integer,
        ForeignKey(
             'ClientInfo.clientid',
             ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    timestamps = Column(ARRAY(DateTime, dimensions=2))
    """
    Timestamps for the glucose data.

    A 2-dimensional array with blocks of data. Each block represents the data
    of one CGM device, which has a lifespan of circa 14 days.

    :type: list(list(datetime.datatime))
    """

    glucose = Column(ARRAY(Float, dimensions=2))
    """
    Glucose data from the GCM.

    A 2-dimensional array with blocks of data. Each block represents the data
    of one CGM device, which has a lifespan of circa 14 days.

    :type: list(list(float))
    """

    activation_timestamp = Column(DateTime)
    """
    Timestamp when last CGM was activated.

    On the CGM device, the time is stored as minutes since activation. It must
    be converted to a timestamp before it can be added to the timestamps array.
    This timestamp can be used to calculate the timestamp for each data point.

    :type: datetime.datetime
    """
