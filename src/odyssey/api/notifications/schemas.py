from marshmallow import Schema, fields, post_dump, validate

from odyssey import ma
from odyssey.api.notifications.models import Notifications, NotificationsPushRegistration
from odyssey.utils.email import push_providers


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notifications
        include_fk = True
        load_instance = True
        exclude = ('created_at', 'updated_at')
        dump_only = ('notification_id', 'user_id')

    # Remove these if not needed by frontend. I don't think they use this information at all.
    @post_dump(pass_original=True)
    def make_object(self, notification_dict, notification_obj, **kwargs):
        notification_dict['notification_type'] = notification_obj.notification_type_obj.notification_type
        notification_dict['is_staff'] = notification_obj.user.is_staff
        return notification_dict


class PushRegistrationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NotificationsPushRegistration
        load_instance = True
        exclude = ('idx', 'created_at', 'updated_at')


class PushRegistrationPostSchema(Schema):
    device_token = fields.String(required=True)
    device_id = fields.String(required=True)
    device_description = fields.String(required=True)
    device_os = fields.String(validate=validate.OneOf(['apple', 'android']), required=True)


class PushRegistrationDeleteSchema(Schema):
    device_token = fields.String(required=True)
