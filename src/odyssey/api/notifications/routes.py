from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource
from sqlalchemy.exc import IntegrityError

from odyssey import db
from odyssey.api import api
from odyssey.api.lookup.models import LookupNotifications
from odyssey.api.notifications.models import Notifications, NotificationsPushRegistration
from odyssey.api.notifications.schemas import NotificationSchema, PushRegistrationSchema
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.errors import InputError, UnknownError

ns = api.namespace('notifications', description='Endpoints for all types of notifications.')

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class NotificationsEndpoint(Resource):

    @token_auth.login_required
    @responds(schema=NotificationSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """ Returns a list of notifications for the given user_id. """
        return Notifications.query.filter_by(user_id=user_id).all()

    @token_auth.login_required
    @accepts(schema=NotificationSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Create a new notification for the user with user_id. """
        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()


@ns.route('/<int:user_id>/<int:notification_id>/')
@ns.doc(params={
    'user_id': 'User ID number',
    'notification_id': 'Notification ID number'})
class NotificationsUpdateEndpoint(Resource):

    @token_auth.login_required
    @accepts(schema=NotificationSchema, api=ns)
    @responds(status_code=200, api=ns)
    def put(self, user_id, notification_id):
        """ Updates the notification specified by the given id number. """

        notification = (
            Notifications
            .query
            .filter_by(
                user_id=user_id,
                notification_id=notification_id)
            .one_or_none())

        if not notification:
            raise InputError(400, 'Wrong notification_id or user_id.')

        request.parsed_obj.user_id = user_id
        request.parsed_obj.notification_id = notification_id
        db.session.merge(request.parsed_obj)
        db.session.commit()


@ns.route('/push/register/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class PushRegistrationEndpoint(Resource):

    @token_auth.login_required
    @responds(schema=PushRegistrationSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """ Get all device IDs for user. """
        return NotificationsPushRegistration.query.filter_by(user_id=user_id).all()

    @token_auth.login_required
    @accepts(schema=PushRegistrationSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Register a new device ID (additive).

        New devices are added to the user, existing devices are not overwritten. Trying to
        add an existing device is silently ignored.
        """
        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        try:
            db.session.commit()
        except IntegrityError:
            pass

    @token_auth.login_required
    @accepts(schema=PushRegistrationSchema, api=ns)
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """ Delete device ID (subtractive). """
        device = (
            NotificationsPushRegistration
            .query
            .filter_by(
                user_id=user_id,
                device_id=request.parsed_obj.device_id)
            .one_or_none())
        if device:
            db.session.delete(device)
            db.session.commit()
