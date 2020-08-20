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

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


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
