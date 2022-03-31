import logging
logger = logging.getLogger(__name__)

from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from sqlalchemy import or_
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.notifications.models import Notifications, NotificationsPushRegistration
from odyssey.api.notifications.schemas import (
    NotificationSchema,
    PushRegistrationDeleteSchema,
    PushRegistrationGetSchema,
    PushRegistrationPostSchema,
    ApplePushNotificationAlertTestSchema,
    ApplePushNotificationBackgroundTestSchema,
    ApplePushNotificationBadgeTestSchema,
    ApplePushNotificationVoipTestSchema)
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.message import PushNotification
from odyssey.utils.files import FileDownload, get_profile_pictures
from odyssey.api.user.models import UserProfilePictures

ns = Namespace('notifications', description='Endpoints for all types of notifications.')

@ns.route('/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class NotificationsEndpoint(BaseResource):

    @token_auth.login_required
    @responds(schema=NotificationSchema(many=True), api=ns, status_code=200)
    def get(self, user_id):
        """ Returns a list of notifications for the given user_id. """
        return Notifications.query.filter_by(user_id=user_id).all()

@ns.route('/<int:user_id>/<int:notification_id>/')
@ns.doc(params={
    'user_id': 'User ID number',
    'notification_id': 'Notification ID number'})
class NotificationsUpdateEndpoint(BaseResource):

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
            raise BadRequest('Wrong notification_id or user_id.')

        request.parsed_obj.user_id = user_id
        request.parsed_obj.notification_id = notification_id
        db.session.merge(request.parsed_obj)
        db.session.commit()


@ns.route('/push/register/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class PushRegistrationEndpoint(BaseResource):
    # Multiple devices per user allowed
    __check_resource__ = False

    @token_auth.login_required
    @responds(schema=PushRegistrationGetSchema(many=True), api=ns, status_code=200)
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

        device_voip_token : str (optional)
            The device token for VoIP notifications. This is used on Apple devices only.

        device_id : str
            A unique number that identifies the device independent of app and OS updates.

        device_description : str
            A description of the device, perhaps device name + OS name and version.

        device_platform : str, one of: apple, android, debug.
            Main OS of the device. Only apple and android are supported at the moment.
            If set to debug, this endpoint will insert an entry into the database, but
            not create and actual AWS SNS notification endpoint. Instead, messages will
            be sent to a debug log.
        """
        device_token = request.json['device_token']
        device_id = request.json['device_id']
        device_description = request.json['device_description']
        device_platform = request.json['device_platform']
        device_voip_token = request.json.get('device_voip_token')
        device_info = {
            'user_id': user_id,
            'device_id': device_id,
            'description': device_description}

        pn = PushNotification()

        device = (
            NotificationsPushRegistration
            .query
            .filter_by(
                user_id=user_id,
                device_id=device_id)
            .one_or_none())
            
        if device:
            # Token may have changed with existing device. Even if token is the same,
            # the endpoint may have been disabled or settings may have changed.
            # Re-registering will fix that.
            device.arn = pn.register_device(
                device_token,
                device_platform,
                device_info=device_info,
                current_endpoint=device.arn)
            if device_voip_token:
                device.voip_arn = pn.register_device(
                    device_voip_token,
                    device_platform,
                    device_info=device_info,
                    current_endpoint=device.voip_arn,
                    voip=True)
            device.device_token = device_token
            device.device_voip_token = device_voip_token
            device.device_description = device_description
        else:
            device = NotificationsPushRegistration(user_id=user_id)
            device.arn = pn.register_device(
                device_token,
                device_platform,
                device_info=device_info)
            if device_voip_token:
                device.voip_arn = pn.register_device(
                    device_voip_token,
                    device_platform,
                    device_info=device_info,
                    voip=True)
            device.device_token = device_token
            device.device_voip_token = device_voip_token
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

        In case of an Apple device, it will unregister both the regular and
        the VoIP tokens. You can pass in either one and both will be
        unregistered at the same time.

        Parameters
        ----------
        device_token : str
            Device token to unregister and delete.
        """
        device_token = request.json['device_token']

        device = (
            NotificationsPushRegistration
            .query
            .filter_by(
                user_id=user_id)
            .filter(
                or_(
                    NotificationsPushRegistration.device_token == device_token,
                    NotificationsPushRegistration.device_voip_token == device_token))
            .one_or_none())

        if device:
            pn = PushNotification()
            pn.unregister_device(device.arn)

            if device.voip_arn:
                pn.unregister_device(device.voip_arn)

            db.session.delete(device)
            db.session.commit()


# Development-only Namespace, sets up endpoints for testing push notifications.
ns_dev = Namespace(
    'notifications',
    path='/notifications/push/test',
    description='[DEV ONLY] Endpoints for testing sending of push notifications.')

@ns_dev.route('/alert/<int:user_id>/')
class ApplePushNotificationAlertTestEndpoint(BaseResource):

    @token_auth.login_required
    @accepts(schema=ApplePushNotificationAlertTestSchema, api=ns_dev)
    @responds(schema=ApplePushNotificationAlertTestSchema, status_code=201, api=ns_dev)
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
        pn = PushNotification()
        msg = pn.send(user_id, 'alert', request.json.get('content', {}))
        return {'message': msg}


@ns_dev.route('/background/<int:user_id>/')
class ApplePushNotificationBackgroundTestEndpoint(BaseResource):

    @token_auth.login_required
    @accepts(schema=ApplePushNotificationBackgroundTestSchema, api=ns_dev)
    @responds(schema=ApplePushNotificationBackgroundTestSchema, status_code=201, api=ns_dev)
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
        pn = PushNotification()
        msg = pn.send(user_id, 'background', request.json.get('content', {}))
        return {'message': msg}


@ns_dev.route('/badge/<int:user_id>/')
class ApplePushNotificationBadgeTestEndpoint(BaseResource):

    @token_auth.login_required
    @accepts(schema=ApplePushNotificationBadgeTestSchema, api=ns_dev)
    @responds(schema=ApplePushNotificationBadgeTestSchema, status_code=201, api=ns_dev)
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
        pn = PushNotification()
        msg = pn.send(user_id, 'badge', request.json.get('content', {}))
        return {'message': msg}


@ns_dev.route('/voip/<int:user_id>/')
class ApplePushNotificationVoipTestEndpoint(BaseResource):

    @token_auth.login_required
    @accepts(schema=ApplePushNotificationVoipTestSchema, api=ns_dev)
    @responds(schema=ApplePushNotificationVoipTestSchema, status_code=201, api=ns_dev)
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
        pn = PushNotification()
        content = request.json.get('content', {})

        if content:
            content['data']['staff_profile_picture'] = get_profile_pictures(content['data']['staff_id'])

        msg = pn.send(user_id, 'voip', content)
        return {'message': msg}
