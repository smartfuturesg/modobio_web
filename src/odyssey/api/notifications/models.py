"""
Database tables for the notifications section of the Modo Bio API.
All tables in this module are prefixed with 'Notifications'.
"""

from datetime import datetime, timedelta

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class Notifications(db.Model):
    """ General information about notifications. """

    __tablename__ = 'Notifications'

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
        unique=False)
    """
    User ID number.

    :type: int, foreign key to :attr:`User.user_id <odyssey.api.models.user.User.user_id>`
    """

    user = db.relationship('User', uselist=False)
    """
    User instance holding user data.

    :type: :class:`User <odyssey.api.user.models.User>` instance
    """

    title = db.Column(db.String(256))
    """
    Title that summarizes this notification.

    :type: str
    """

    content = db.Column(db.String(2048))
    """
    The main body of this notification.

    :type: str
    """

    action = db.Column(db.String(512))
    """
    The result of clicking this notification - either hyperlink or code function

    :type: str
    """

    time_to_live = db.Column(db.Integer)
    """
    The lifetime of the notification in seconds. If None, the notification does not expire.
    If both :attr:`time_to_live` and :attr:`expires` are set, then :attr:`time_to_live` is
    ignored.

    :type: int or None
    :unit: seconds
    """

    expires = db.Column(db.DateTime)
    """
    The time this notification will expire. If :attr:`time_to_live` is set and :attr:`expires`
    is not set, then :attr:`expires` will be calculated from :attr:`time_to_live`. If both are
    None, the notification will not expire.

    :type: :class:`datetime` or None
    """

    read = db.Column(db.Boolean, server_default='f')
    """
    Whether the user has read this notification.

    :type: bool
    """

    deleted = db.Column(db.Boolean, server_default='f')
    """
    Whether the user has deleted this notification. This will not remove the entry from
    the database, but can be used to hide this notification in a UI.

    :type: bool
    """

    notification_type_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'LookupNotifications.notification_type_id',
            ondelete='cascade'),
        nullable=False,
        unique=False)
    """
    Foreign key to notification_type_id in the LookupNotifications table.

    :type: int, foreign key to :attr:`LookupNotifications.notification_type_id <odyssey.api.notifications.lookup.models.LookupNotifications.notifications_type_id>`
    """

    # Should have been called notification_type, but that needs to be set in schema.
    notification_type_obj = db.relationship(
        'LookupNotifications',
        uselist=False)
    """
    LookupNotification instance holding notification type data linked to this notification.

    :type: :class:`LookupNotification <odyssey.api.lookup.models.LookupNotification>` instance
    """


@db.event.listens_for(Notifications, "after_insert")
def set_expiry(mapper, connection, target):
    """ Set expiry timestamp from time_to_live.

    Parameters
    ----------
    mapper : ???
        What does this do? Not used.

    connection : :class:`sqlalchemy.engine.Connection`
        Connection to the database engine.

    target : :class:`sqlalchemy.schema.Table`
        Specifically :class:`Notifications`
    """
    if target.time_to_live and not target.expires:
        expires = datetime.utcnow() + timedelta(seconds=target.time_to_live)
        connection.execute(
            Notifications.__table__.update().where(Notifications.notification_id == target.notification_id).values(expires=expires)
        )


class NotificationsPushRegistration(db.Model):
    """ Table for registering devices for push notifications. """

    __tablename__ = 'NotificationsPushRegistration'

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
        unique=False)
    """
    User ID number.

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    user = db.relationship('User', uselist=False)
    """
    User instance holding user data.

    :type: :class:`User <odyssey.api.user.models.User>` instance
    """

    device_token = db.Column(db.String(1024))
    """
    Device token (registration ID on Android) provided by the OS to enable
    push notifications.

    :type: str, max length 1024
    """

    device_id = db.Column(db.String(1024))
    """
    Unique identifier that identifies a device and persists across installations
    of the app. Needed to distighuish changing device tokens on one device from
    having multiple devices.

    :type: str, max length 1024
    """

    device_description = db.Column(db.String(1024))
    """
    Description of device (phone name, os version, etc.).

    :type: str, max length 1024
    """

    channel = db.Column(db.String(25))
    """
    Name of the channel of the push notification service. AWS calls
    this the "platform application". Currently 'APNS' for Apple Push
    Notification Service, 'APNS_VOIP' for Apple video call start, or
    'FCM' for Firebase/Google Cloud Messaging.

    :type: str, max length 25
    """

    arn = db.Column(db.String(256))
    """
    The AWS Resource Name (ARN) of the notification channel (AWS SNS
    platform application).

    :type: str, max length 256
    """
