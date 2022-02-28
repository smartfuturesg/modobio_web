from marshmallow import (
    Schema,
    fields
)
from datetime import datetime
from flask import current_app
from pytz import timezone
import logging

logger = logging.getLogger(__name__)


class MaintenanceBlocksCreateSchema(Schema):
    # Must be DateTime objects in the future
    start_time = fields.DateTime(format="iso", required=True, validate=lambda x: x.replace(tzinfo=timezone(current_app.config['MAINTENANCE_TIMEZONE'])) > datetime.now(
        tz=timezone(current_app.config['MAINTENANCE_TIMEZONE'])))
    end_time = fields.DateTime(format="iso", required=True, validate=lambda x: x.replace(tzinfo=timezone(current_app.config['MAINTENANCE_TIMEZONE'])) > datetime.now(
        tz=timezone(current_app.config['MAINTENANCE_TIMEZONE'])))
    comments = fields.String()


class MaintenanceBlocksDeleteSchema(Schema):
    block_id = fields.UUID(required=True)
    # comments = fields.String(required=False)
