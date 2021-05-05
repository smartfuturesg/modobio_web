from marshmallow import Schema, fields

from odyssey import ma
from odyssey.api.notifications.models import Notifications, NotificationsPush

class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notifications
        load_instance = True
        exclude = ('created_at', 'updated_at')
        dump_only = ('idx', 'user_id', 'is_staff', 'time_to_live')

    #comes from LookupNotifications.type
    notification_type = fields.String(dump_only=True)
    notification_type_id = fields.Integer(dump_only=True)

class PushNotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NotificationsPush
        load_instance = True
        fields = ('device_id',)
