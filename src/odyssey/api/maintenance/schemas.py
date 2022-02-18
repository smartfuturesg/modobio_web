from marshmallow import (
    Schema,
    fields
)
from datetime import datetime
from flask import current_app
import pytz
import logging

logger = logging.getLogger(__name__)


class MaintenanceBlocksCreateSchema(Schema):
    # Must be DateTime objects in the future
    start_time = fields.DateTime(format="iso", required=True, validate=lambda x: x > datetime.now(
        tz=pytz.timezone(current_app.config['TIMEZONE'])))
    end_time = fields.DateTime(format="iso", required=True, validate=lambda x: x > datetime.now(
        tz=pytz.timezone(current_app.config['TIMEZONE'])))
    comments = fields.String()


class MaintenanceBlocksDeleteSchema(Schema):
    block_id = fields.UUID(required=True)
    # comments = fields.String(required=False)
