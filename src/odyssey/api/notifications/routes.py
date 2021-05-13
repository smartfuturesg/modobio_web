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
    ApplePushNotificationSchema,
    PushRegistrationSchema,
    PushRegistrationDeleteSchema,
    PushRegistrationPostSchema)
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import DB_SERVER_TIME
from odyssey.utils.email import push_providers, register_device, unregister_device
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
        """ Register a new device token.

        Parameters
        ----------
        device_token : str
            The device token (called registration ID on Android) obtained from the OS to allow
            push notifications.

        device_id : str
            A unique number that identifies the device independent of app and OS updates.

        device_description : str
            A description of the device, perhaps device name + OS name and version.

        device_os : str, one of: apple, android
            Main OS of the device. Only apple and android are supported at the moment.
        """
        device_token = request.json['device_token']
        device_id = request.json['device_id']
        device_description = request.json['device_description']
        device_os = request.json['device_os']
        device_str = f'{device_id}/{device_description}'

        providers = push_providers[device_os]

        for prov in providers:
            # Check if combination of device_token/device_id/provider already exists.
            device = (
                NotificationsPushRegistration
                .query
                .filter_by(
                    user_id=user_id,
                    device_token=device_token,
                    device_id=device_id,
                    provider=prov)
                .one_or_none())

            if device:
                continue

            # Check if device_id (with different token) already exists.
            device = (
                NotificationsPushRegistration
                .query
                .filter_by(
                    user_id=user_id,
                    device_id=device_id,
                    provider=prov)
                .one_or_none())

            if device:
                device.arn = register_device(device_token, device_str, prov, current_endpoint=device.arn)
                device.device_token = device_token
                device.device_description = device_description
            else:
                device = NotificationsPushRegistration(user_id=user_id)
                device.arn = register_device(device_token, device_str, prov)
                device.device_token = device_token
                device.device_id = device_id
                device.device_description = device_description
                device.provider = prov
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
            .all())
        if device:
            for dev in device:
                unregister_device(dev.arn)
                db.session.delete(dev)
            db.session.commit()


import os
if os.getenv('FLASK_ENV') != 'production':
    from odyssey.utils.email import push_notification, NotificationType, NotificationProvider
    from marshmallow import INCLUDE

    ntype_doc = '\n'.join([f'                - {x.name}: {x.value}' for x in NotificationType])
    nprov_doc = '\n'.join([f'                - {x.name}' for x in NotificationProvider])

    @ns.route('/push/test/<int:user_id>/')
    @ns.doc(security=None)
    class PushTestEndpoint(Resource):

        # @token_auth.login_required
        @accepts(schema=ApplePushNotificationSchema, api=ns)
        @responds(schema=ApplePushNotificationSchema, status_code=201, api=ns)
        def post(self, user_id):
            """ Send notification to user.

            This endpoint is only available in **dev** environments.

            Parameters
            ----------

            type : str
                What type of notification to send, one of:
{ntype_doc}

            provider : str
                Send push notificaton through this service, one of:
{nprov_doc}

            kwargs
                All other parameters are used in the message. Depends on type of message.

            Returns
            -------
            str
                The json encoded message as send to the service.
            """
            ntype = request.json['type']
            prov = request.json['provider']
            contents = request.json.get('contents', {})
            out = push_notification(user_id, ntype, prov, **contents)
            return out

        post.__doc__ = post.__doc__.format(ntype_doc=ntype_doc, nprov_doc=nprov_doc)
