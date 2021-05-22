from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource
from sqlalchemy.exc import IntegrityError

from odyssey import db
from odyssey.api import api
from odyssey.api.lookup.models import LookupNotifications
from odyssey.api.notifications.models import Notifications, NotificationsPushRegistration
from odyssey.api.notifications.schemas import (
    NotificationSchema,
    PushRegistrationSchema,
    PushRegistrationDeleteSchema,
    PushRegistrationPostSchema)
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.message import push_platforms, register_device, unregister_device
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
        """ Get all device tokens for user. """
        return NotificationsPushRegistration.query.filter_by(user_id=user_id).all()

    @token_auth.login_required
    @accepts(schema=PushRegistrationPostSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """ Register a new device.

        Parameters
        ----------
        device_token : str
            The device token (called registration ID on Android) obtained from the OS to allow
            push notifications.

        device_id : str
            A unique number that identifies the device independent of app and OS updates.

        device_description : str
            A description of the device, perhaps device name + OS name and version.

        device_os : str, one of: apple, android, debug.
            Main OS of the device. Only apple and android are supported at the moment.
            If set to debug, this endpoint will insert an entry into the database, but
            not create and actual AWS SNS notification endpoint. Instead, messages will
            be sent to a debug log.
        """
        device_token = request.json['device_token']
        device_id = request.json['device_id']
        device_description = request.json['device_description']
        device_os = request.json['device_os']
        device_str = f'user: {user_id}, device: {device_id}, description: {device_description}'

        device = (
            NotificationsPushRegistration
            .query
            .filter_by(
                user_id=user_id,
                device_id=device_id)
            .one_or_none())

        if device:
            # Re-register a device, token may have changed. Even if token is the same,
            # the endpoint may have been disables or settings may have changed.
            # Re-registering will fix that.
            device.arn = register_device(device_token, device_os, device_str, current_endpoint=device.arn)
            device.device_token = device_token
            device.device_description = device_description
        else:
            device = NotificationsPushRegistration(user_id=user_id)
            device.arn = register_device(device_token, device_os, device_str)
            device.device_token = device_token
            device.device_id = device_id
            device.device_description = device_description
            db.session.add(device)

        db.session.commit()

    @token_auth.login_required
    @accepts(schema=PushRegistrationDeleteSchema, api=ns)
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """ Delete device token.

        Unregisters device token, not entire device, from the AWS SNS service
        for all topics. Then deletes device token entries from database.

        Parameters
        ----------
        device_token : str
            Device token to unregister and delete.
        """
        device = (
            NotificationsPushRegistration
            .query
            .filter_by(
                user_id=user_id,
                device_token=request.json['device_token'])
            .one_or_none())
        if device:
            unregister_device(device.arn)
            db.session.delete(device)
            db.session.commit()


import os
# TODO: fix this after ticket NRV-1838 is done.
if os.getenv('FLASK_ENV') != 'production':
    from odyssey.utils.message import push_notification, NotificationType
    from odyssey.api.notifications.schemas import (
        ApplePushNotificationAlertTestSchema,
        ApplePushNotificationBackgroundTestSchema,
        ApplePushNotificationBadgeTestSchema,
        ApplePushNotificationVoipTestSchema)

    @ns.route('/push/test/alert/<int:user_id>/')
    @ns.doc(params={'user_id': 'User ID number'})
    class PushTestAlertEndpoint(Resource):

        @token_auth.login_required
        @accepts(schema=ApplePushNotificationAlertTestSchema, api=ns)
        @responds(schema=ApplePushNotificationAlertTestSchema, status_code=201, api=ns)
        def post(self, user_id):
            """ [DEV ONLY] Send an alert notification to the user.

            Note
            ----
            **This endpoint is only available in DEV environments.**

            Parameters
            ----------
            content : dict
                The contents of the message.

            Returns
            -------
            dict
                The json encoded message as send to the service.
            """
            msg = push_notification(user_id, 'alert', request.json.get('content', {}))
            return {'message': msg}


    @ns.route('/push/test/background/<int:user_id>/')
    @ns.doc(params={'user_id': 'User ID number'})
    class PushTestBackgroundEndpoint(Resource):

        @token_auth.login_required
        @accepts(schema=ApplePushNotificationBackgroundTestSchema, api=ns)
        @responds(schema=ApplePushNotificationBackgroundTestSchema, status_code=201, api=ns)
        def post(self, user_id):
            """ [DEV ONLY] Send a background update notification to the user.

            Note
            ----
            **This endpoint is only available in DEV environments.**

            Parameters
            ----------
            content : dict
                The contents of the message.

            Returns
            -------
            dict
                The json encoded message as send to the service.
            """
            msg = push_notification(user_id, 'background', request.json.get('content', {}))
            return {'message': msg}


    @ns.route('/push/test/badge/<int:user_id>/')
    @ns.doc(params={'user_id': 'User ID number'})
    class PushTestBadgeEndpoint(Resource):

        @token_auth.login_required
        @accepts(schema=ApplePushNotificationBadgeTestSchema, api=ns)
        @responds(schema=ApplePushNotificationBadgeTestSchema, status_code=201, api=ns)
        def post(self, user_id):
            """ [DEV ONLY] Send a badge update notification to the user.

            Note
            ----
            **This endpoint is only available in DEV environments.**

            Parameters
            ----------
            content : dict
                The contents of the message.

            Returns
            -------
            dict
                The json encoded message as send to the service.
            """
            msg = push_notification(user_id, 'badge', request.json.get('content', {}))
            return {'message': msg}

    @ns.route('/push/test/voip/<int:user_id>/')
    @ns.doc(params={'user_id': 'User ID number'})
    class PushTestVoipEndpoint(Resource):

        @token_auth.login_required
        @accepts(schema=ApplePushNotificationVoipTestSchema, api=ns)
        @responds(schema=ApplePushNotificationVoipTestSchema, status_code=201, api=ns)
        def post(self, user_id):
            """ [DEV ONLY] Send a voip initiation notification to the user.

            Note
            ----
            **This endpoint is only available in DEV environments.**

            Parameters
            ----------
            content : dict
                The contents of the message.

            Returns
            -------
            dict
                The json encoded message as send to the service.
            """
            msg = push_notification(user_id, 'voip', request.json.get('content', {}))
            return {'message': msg}
