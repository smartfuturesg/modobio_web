"""
Database tables for the notifications section of the Modo Bio API.
All tables in this module are prefixed with 'Notifications'.
"""

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class Notifications(db.Model):
    """ General information about notifications. """

    __tablename__ = 'Notifications'

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

    notification_type_id = db.Column(
        db.Integer,
        db.ForeignKey('LookupNotifications.notification_type_id'),
        nullable=False)
    """
    Denotes what type of notification this is as defined in the LookupNotifications table.

    :type: int, foreign key('LookupNotifications.notification_id')
    """

    title = db.Column(db.String)
    """
    Title that summarizes this notification.

    :type: str
    """

    content = db.Column(db.String)
    """
    The main body of this notification.

    :type: str
    """

    action = db.Column(db.String)
    """
    The result of clicking this notification - either hyperlink or code function

    :type: str
    """

    expire = db.Column(db.DateTime)
    """
    The time this notification will expire on the user's UI. If null, the notification will not expire.

    :type: datetime
    """

    is_staff = db.Column(db.Boolean)
    """
    Whether this notification is for the client or staff portion of the user's account.

    :type: bool
    """

    read = db.Column(db.Boolean)
    """
    Whether the user has read this notification.

    :type: bool
    """

    deleted = db.Column(db.Boolean)
    """
    Whether the user has deleted this notification. This will not remove the entry from
    the database, but can be used to hide this notification in a UI.

    :type: bool
    """


class NotificationsPush(db.Model):
    """ Table for push notifications. """

    __tablename__ = 'NotificationsPush'

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

    device_id = db.Column(db.String(1024), unique=True)
    """
    Device ID number, the unique string that identifies the device
    for which push notifications are enabled.

    :type: str, unique
    """

    # channel_maybe = db.Column(db.String(1024))
    # os_maybe = db.Column(db.String(1024))
