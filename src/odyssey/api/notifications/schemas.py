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


class PushRegistrationGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NotificationsPushRegistration
        load_instance = True
        exclude = ('idx', 'created_at', 'updated_at')


class PushRegistrationPostSchema(Schema):
    device_token = fields.String(required=True)
    device_voip_token = fields.String(required=False)
    device_id = fields.String(required=True)
    device_description = fields.String(required=True)
    # I want to use PushNotifications.platforms.keys() here, but cannot import
    # PushNotifications from odyssey.utils.message because of circular dependency.
    device_os = fields.String(required=True, validate=validate.OneOf(['apple', 'android', 'debug']))


class PushRegistrationDeleteSchema(Schema):
    device_token = fields.String(required=True)


class SkipNoneSchema(Schema):
    @pre_dump
    def skip_none(self, data: dict, many: bool=False) -> dict:
        """ Removes all keys with values = None from dict.

        Also removes empty dicts and empty lists.

        Parameters
        ----------
        data : dict
            Input dictionary with possible None values.

        many : bool, default = False
            The :attr:`marshmallow.fields.Field.many` parameter. Not used in this function.

        Returns
        -------
        dict
            A copy of the input dictionary with None values and empty dictionaries removed.
        """
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


class HyphenSchema(Schema):
    def hyphenate(self, string: str) -> str:
        """ Convert underscores to hyphens in a string.

        Parameters
        ----------
        string : str
            Input string with underscores.

        Returns
        -------
        str
            A copy of the input string with underscores replaced with hyphens.
        """
        return string.replace('_', '-')

    def on_bind_field(self, field_name: str, field_obj: fields.Field):
        """ Change field name.

        On field creation, convert underscored fieldnames (valid Python) to hyphenated
        names (required output). This method will be called automatically by the
        :mod:`marshmallow` field binding process.

        Parameters
        ----------
        field_name : str
            Name of the field as defined in Python.

        field_obj : :class:`marshmallow.fields.Field`
            The instance of :class:`marshmallow.fields.Field` that will be bound to this
            parameter.
        """
        field_obj.data_key = self.hyphenate(field_obj.data_key or field_name)


class CamelCaseSchema(Schema):
    def camelcase(self, string: str) -> str:
        """ Convert underscores to a camelCase string.

        Parameters
        ----------
        string : str
            Input string with underscores.

        Returns
        -------
        str
            A copy of the input string turned into camelCase.
        """
        parts = iter(string.split('_'))
        return next(parts) + ''.join(p.title() for p in parts)

    def on_bind_field(self, field_name: str, field_obj: fields.Field):
        """ Change field name.

        On field creation, convert underscored fieldnames to camelCase names.
        This method will be called automatically by the :mod:`marshmallow` field
        binding process.

        Parameters
        ----------
        field_name : str
            Name of the field as defined in Python.

        field_obj : :class:`marshmallow.fields.Field`
            The instance of :class:`marshmallow.fields.Field` that will be bound to this
            parameter.
        """
        field_obj.data_key = self.camelcase(field_obj.data_key or field_name)


# See https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW1

# Nested schemas
#
# The following are for validation in utils/message.py
#
# APNAlertS(APNAlertPartS(APNAlertBodyS)))
# APNBackgroundS(APNBackgroundPartS))
# APNBadgeS(APNBadgePartS))
# APNVoipS(APNVoipDataS)
#
# For test endpoints, the above are wrapped in test schemas:
#
# APNAlertTestS(APNAlertS)
# APNBackgroundTestS(APNBackgroundS)
# APNBadgeTestS(APNBadgeS)
# APNVoipTestS(APNVoipS)


class ApplePushNotificationAlertBodySchema(SkipNoneSchema, HyphenSchema):
    title = fields.String(required=True, validate=validate.Length(1, 25))
    body = fields.String(required=True, validate=validate.Length(1, 3800))
    title_loc_key = fields.String(missing=None)
    title_loc_args = fields.List(fields.String(), missing=None)
    action_loc_key = fields.String(missing=None)
    loc_key = fields.String(missing=None)
    loc_args = fields.List(fields.String(), missing=None)
    launch_image = fields.String(missing=None)


class ApplePushNotificationAlertPartSchema(SkipNoneSchema, HyphenSchema):
    alert = fields.Nested(ApplePushNotificationAlertBodySchema, required=True)
    badge = fields.Integer(missing=None)
    sound = fields.String(missing=None)
    category = fields.String(missing=None)
    thread_id = fields.String(missing=None)


class ApplePushNotificationBackgroundPartSchema(SkipNoneSchema, HyphenSchema):
    class Meta:
        unknown = EXCLUDE

    content_available = fields.Integer(required=True, default=1, validate=validate.Equal(1))


class ApplePushNotificationBadgePartSchema(SkipNoneSchema, HyphenSchema):
    badge = fields.Integer(required=True)
    sound = fields.String(missing=None)


class ApplePushNotificationAlertSchema(SkipNoneSchema, HyphenSchema):
    class Meta:
        unknown = INCLUDE

    aps = fields.Nested(ApplePushNotificationAlertPartSchema)


class ApplePushNotificationBackgroundSchema(SkipNoneSchema, HyphenSchema):
    class Meta:
        unknown = INCLUDE

    aps = fields.Nested(ApplePushNotificationBackgroundPartSchema)


class ApplePushNotificationBadgeSchema(SkipNoneSchema, HyphenSchema):
    class Meta:
        unknown = INCLUDE

    aps = fields.Nested(ApplePushNotificationBadgePartSchema)


class ApplePushNotificationAlertTestSchema(SkipNoneSchema, HyphenSchema):
    # Input
    content = fields.Nested(ApplePushNotificationAlertSchema, load_only=True)

    # Output
    message = fields.Dict(dump_only=True)


class ApplePushNotificationBackgroundTestSchema(SkipNoneSchema, HyphenSchema):
    # Input
    content = fields.Nested(ApplePushNotificationBackgroundSchema, load_only=True)

    # Output
    message = fields.Dict(dump_only=True)


class ApplePushNotificationBadgeTestSchema(SkipNoneSchema, HyphenSchema):
    # Input
    content = fields.Nested(ApplePushNotificationBadgeSchema, load_only=True)

    # Output
    message = fields.Dict(dump_only=True)


# The next three schemas are not dictated by Apple, but by the frontend.
class ApplePushNotificationVoipDataSchema(SkipNoneSchema):
    booking_id = fields.Integer(required=True)
    booking_description = fields.String(missing=None)
    staff_id = fields.Integer(required=True)
    staff_first_name = fields.String(required=True)
    staff_middle_name = fields.String(missing=None)
    staff_last_name = fields.String(required=True)


class ApplePushNotificationVoipSchema(Schema):
    class Meta:
        unknown = INCLUDE

    type = fields.String(default='incoming-call', required=True, validate=validate.Equal('incoming-call'))
    data = fields.Nested(ApplePushNotificationVoipDataSchema, required=True)


class ApplePushNotificationVoipTestSchema(SkipNoneSchema):
    # Input
    content = fields.Nested(ApplePushNotificationVoipSchema, load_only=True)

    # Output
    message = fields.Dict(dump_only=True)
