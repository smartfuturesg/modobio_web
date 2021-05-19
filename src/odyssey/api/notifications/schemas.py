from marshmallow import (
    fields,
    INCLUDE,
    EXCLUDE,
    pre_dump,
    pre_load,
    post_dump,
    post_load,
    Schema,
    validate,
    ValidationError)

from odyssey import ma
from odyssey.api.notifications.models import Notifications, NotificationsPushRegistration
from odyssey.utils.email import NotificationType, push_platforms


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
    device_os = fields.String(validate=validate.OneOf(push_platforms.keys()), required=True)


class PushRegistrationDeleteSchema(Schema):
    device_token = fields.String(required=True)


class ApplePushNotificationBaseSchema(Schema):
    @pre_dump
    def skip_none(self, data: dict, many: bool=False) -> dict:
        if isinstance(data, dict):
            newdata = {k: self.skip_none(v) for k, v in data.items() if v is not None}
            if newdata:
                return newdata
        elif isinstance(data, (list, tuple)):
            # This list comprehention should also include a 'if i is not None' clause,
            # just like dict. But [None, None, 'x', None] is not the same list as
            # ['x']. And should a list [None, None, None] reduce to [], which is then
            # removed entirely?
            newdata = [self.skip_none(i) for i in data]
            if newdata:
                return newdata
        return data

    def hyphenate(self, string: str) -> str:
        return string.replace('_', '-')

    # def on_bind_field(self, field_name, field_obj):
    #     field_obj.data_key = self.hyphenate(field_obj.data_key or field_name)


class ApplePushNotificationAlertSchema(ApplePushNotificationBaseSchema):
    title = fields.String(required=True, validate=validate.Length(1, 5))
    body = fields.String(required=True, validate=validate.Length(1, 3800))
    title_loc_key = fields.String()
    title_loc_args = fields.List(fields.String())
    action_loc_key = fields.String()
    loc_key = fields.String()
    loc_args = fields.List(fields.String())
    launch_image = fields.String()


class ApplePushNotificationContentSchema(ApplePushNotificationBaseSchema):
    alert = fields.Nested(ApplePushNotificationAlertSchema)
    badge = fields.Integer()
    sound = fields.String()
    content_available = fields.Integer(validate=validate.Equal(1))
    category = fields.String()
    thread_id = fields.String()


class ApplePushNotificationSchema(ApplePushNotificationBaseSchema):
    # See https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/
    # RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW1
    class Meta:
        unknown = INCLUDE

    # Input
    notification_type = fields.String(
        required=True,
        load_only=True,
        validate=validate.OneOf([x.name for x in NotificationType]))
    contents = fields.Dict(load_only=True)

    # Output
    aps = fields.Nested(ApplePushNotificationContentSchema, dump_only=True)
