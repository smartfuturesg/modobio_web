from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.api import api
from odyssey.api.lookup.models import LookupNotifications
from odyssey.api.notifications.models import Notifications, NotificationsPush
from odyssey.api.notifications.schemas import NotificationSchema, PushNotificationSchema
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.errors import InputError

ns = api.namespace('notifications', description='Endpoints for all types of notifications.')

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class NotificationsEndpoint(Resource):

    @token_auth.login_required
    @responds(schema=NotificationSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """ Returns a list of notifications for the given user_id. """

        notifications = Notifications.query.filter_by(user_id=user_id).all()

        for notification in notifications:
                notification.notification_type = LookupNotifications.query.filter_by(notification_type_id=notification.notification_type_id).one_or_none().notification_type

        return notifications


@ns.route('/<int:notification_id>/')
@ns.doc(params={'notification_id': 'Notification ID number'})
class NotificationsUpdateEndpoint(Resource):

    @token_auth.login_required
    @accepts(schema=NotificationSchema, api=ns)
    @responds(schema=NotificationSchema, api=ns, status_code=201)
    def put(self, notification_id):
        """ Updates the notification specified by the given id number. """

        notification = Notifications.query.filter_by(idx=notification_id).one_or_none()

        if not notification:
            raise InputError(400, 'Invalid notification id.') 

        notification.update(request.json)
        db.session.commit()

        notification.notification_type = LookupNotifications.query.filter_by(notification_type_id=notification.notification_type_id).one_or_none().notification_type

        return notification


@ns.route('/push/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class PushNotificationsEndpoint(Resource):

    @token_auth.login_required(user_type=('client',))
    @responds(schema=PushNotificationSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """ Get all device IDs for user. """
        pass

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=PushNotificationSchema, api=ns)
    def post(self, user_id):
        """ Register a new device ID (additive). """
        pass

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=PushNotificationSchema, api=ns)
    def delete(self, user_id):
        """ Delete device ID (subtractive). """
        pass
