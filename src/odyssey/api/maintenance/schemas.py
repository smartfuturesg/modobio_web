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
    # Reason for maintenance, corresponding to an item in the prod_maintenance_reasons DDB table
    reason_id = fields.Integer(required=True)
    # Comments = any additional notes; Will not be displayed by front end
    comments = fields.String()


class MaintenanceBlocksDeleteSchema(Schema):
    block_id = fields.UUID(required=True)
    # comments = fields.String(required=False)
