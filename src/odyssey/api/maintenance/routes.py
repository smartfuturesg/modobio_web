import logging
import time
import pytz
import uuid
import boto3
from datetime import datetime, timedelta, time
from flask import current_app, request
from flask_accepts import accepts, responds
from odyssey.api import api
from odyssey.api.maintenance.schemas import MaintenanceBlocksDeleteSchema
from odyssey.api.maintenance.schemas import MaintenanceBlocksCreateSchema
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.integrations.instamed import cancel_telehealth_appointment
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from werkzeug.exceptions import BadRequest
from sqlalchemy import and_, or_, select
from odyssey.utils.misc import get_time_index

logger = logging.getLogger(__name__)


ns = api.namespace(
    'maintenance', description='Endpoints for functions related to maintenance scheduling.')


@ns.route('/schedule/')
class MaintenanceApi(BaseResource):
    def is_maint_time_allowed(self) -> bool:
        """
        Check if the given maintenance time is allowed given Modobio's policies:
        - For maintenance between the hours of 6am and 11pm, there must be more
        than 14 days of notice
        - For maintenance between the hours of 11pm and 6am, there must be more
        than 2 days of notice
        """
        # Set timezone based on environment variable
        zone = pytz.timezone(current_app.config['MAINTENANCE_TIMEZONE'])
        # Get and set relevant times, force their timezone info
        # Start and End of the maintenance block, as defined by the user
        start = datetime.fromisoformat(request.json['start_time']).replace(tzinfo=zone)
        end = datetime.fromisoformat(request.json['end_time']).replace(tzinfo=zone)
        # Start and End of business hours, as defined by Modobio
        business_start_hr = current_app.config['BUSINESS_HRS_START']
        business_end_hr = current_app.config['BUSINESS_HRS_END']
        # Now as defined by... the authors of datetime, I guess
        now = datetime.now(tz=zone)

        # Time Deltas
        short_notice = timedelta(days=current_app.config['MAINT_SHORT_NOTICE'])
        std_notice = timedelta(days=current_app.config['MAINT_STD_NOTICE'])
        # Start of the business hours window
        business_start = datetime.combine(start, time(hour=business_start_hr)).replace(tzinfo=zone)

        # If the maintenance start is before the end
        if start < end:
            # If the start time is more than the standard notice window away, both overnight and business maintenance are allowed
            if start > now + std_notice:
                return True
            # If it's at least further away than the short notice window
            elif start > now + short_notice:
                # If the defined business hours time window goes over midnight...
                if business_end_hr < business_start_hr:
                    # ...add a day to the business end datetime
                    business_end = datetime.combine(end + timedelta(days=1), time(hour=business_end_hr)).replace(tzinfo=zone)
                else:
                    # Business start and end are the same day
                    business_end = datetime.combine(end, time(hour=business_end_hr)).replace(tzinfo=zone)

                # If neither 'start' nor 'end' is in business hours, the requested maintenenace block is allowed
                if not business_start < start < business_end and not business_start < end < business_end:
                    return True
        # If all else fails
        return False


    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def get(self):
        """
        Get a list of all maintenance block from DynamoDB.
        """
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(current_app.config['MAINTENANCE_DYNAMO_TABLE'])

        response = table.scan()
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise BadRequest(f'AWS returned the following error: {response["ResponseMetadata"]["Message"]}')

        return response['Items']

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    @accepts(schema=MaintenanceBlocksCreateSchema, api=ns)
    def post(self):
        """
        Create a new maintenance block using the given start_time, end_time, and comments.

        'start_time' and 'end_time' must be iso formatted, UTC datetimes. e.g. 2022-04-23T13:30:00.000000-00:00
        """
        if not self.is_maint_time_allowed():
            raise BadRequest('Maintenance time is not allowed')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(current_app.config['MAINTENANCE_DYNAMO_TABLE'])

        # Set timezone
        zone = pytz.timezone(current_app.config['MAINTENANCE_TIMEZONE'])

        # Set start and end times to the designated timezone for DB storage
        start = datetime.fromisoformat(request.json["start_time"]).replace(tzinfo=zone).astimezone(zone)
        end = datetime.fromisoformat(request.json["end_time"]).replace(tzinfo=zone).astimezone(zone)

        # Get the current users token auth info
        user, _ = token_auth.current_user()
        user_id = str(user.user_id)

        data = {
            'block_id': str(uuid.uuid4()),
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'created_by': user_id,
            'created_at': datetime.now(tz=zone).isoformat(),
            'deleted': "False",
            'updated_by': None,
            'updated_at': None,
            'comments': request.json['comments']
        }

        response = table.put_item(Item=data)
        # If the request to DynamoDB wasn't successful, print out the entire response to help diagnose
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise BadRequest(f'AWS returned the following error: {response["ResponseMetadata"]["Message"]}')

        sm_start = request.json["start_time"]
        sm_end = request.json["end_time"]
        sm_start = datetime.fromisoformat(sm_start)
        sm_end = datetime.fromisoformat(sm_end)
        target_time_window_start = get_time_index(sm_start)
        target_time_window_end = get_time_index(sm_end)

        # find all accepted bookings who have not been notified yet
        bookings_to_cancel = TelehealthBookings.query
        if target_time_window_start > target_time_window_end:
            # this will happen from 22:00 to 23:55
            # in this case, we have to query across two dates
            bookings_to_cancel = \
                bookings_to_cancel.filter(
                    or_(
                        and_(
                            TelehealthBookings.booking_window_id_start_time_utc >= target_time_window_start,
                            TelehealthBookings.target_date_utc == sm_start.date()
                        ),
                        and_(
                            TelehealthBookings.booking_window_id_start_time_utc <= target_time_window_end,
                            TelehealthBookings.target_date_utc == sm_end.date()
                        )
                    )
                ).all()
        else:
            # otherwise just query for bookings whose start id falls between the target times on for today
            bookings_to_cancel = \
                bookings_to_cancel.filter(
                    and_(
                        TelehealthBookings.booking_window_id_start_time_utc >= target_time_window_start,
                        TelehealthBookings.booking_window_id_start_time_utc <= target_time_window_end,
                        TelehealthBookings.target_date_utc == sm_end.date()
                    )
                ).all()

        # cancel each of them
        for booking in bookings_to_cancel:
            cancel_telehealth_appointment(booking, False, 'Conflicted with newly scheduled server maintenance')

        logger.info(f'Scheduled maintenance for {request.json["start_time"]} to {request.json["end_time"]}')

        # If it was successful, return the newly created block
        # Returning data since it allows the user to see the block_id that was created without having to perform a
        # subsequent scan request on the database
        return {"block_id": data["block_id"]}

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    @accepts(schema=MaintenanceBlocksDeleteSchema, api=ns)
    @responds(status_code=200, api=ns)
    def delete(self):
        """
        Set 'deleted' flag to 'True' for a maintenance block with the given 'block_id'.
        """
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(current_app.config['MAINTENANCE_DYNAMO_TABLE'])

        # Set timezone
        zone = pytz.timezone(current_app.config['MAINTENANCE_TIMEZONE'])

        # Get the current users token auth info
        user, _ = token_auth.current_user()
        user_id = str(user.user_id)

        # Deletion process
        # Query using the primary index 'block_id'
        # Add a 'deleted' flag to the block along with update info
        response = table.update_item(
            Key={
                'block_id': request.json['block_id']
            },
            UpdateExpression="set #deleted = :deleted, #updated_by = :updated_by, #updated_at = :updated_at",
            ExpressionAttributeNames={
                '#deleted': 'deleted',
                '#updated_by': 'updated_by',
                '#updated_at': 'updated_at'
            },
            ExpressionAttributeValues={
                ':deleted': "True",
                ':updated_by': user_id,
                ':updated_at': datetime.now(tz=zone).isoformat()
            },
            ReturnValues="UPDATED_NEW"
        )

        # If the request to DynamoDB wasn't successful, print out the entire response to help diagnose
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise BadRequest(f'AWS returned the following error: {response["ResponseMetadata"]["Message"]}.')

        logger.info(f'Scheduled maintenance with block_id: {request.json["block_id"]} was deleted.')
        