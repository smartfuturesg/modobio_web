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
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from werkzeug.exceptions import BadRequest


logger = logging.getLogger(__name__)


ns = api.namespace(
    'maintenance', description='Endpoints for functions related to maintenance scheduling.')


@ns.route('/schedule/')
class MaintenanceApi(BaseResource):
    """
    Functions encompassing DynamoDB functionality.
    """
    def is_maint_time_allowed(self) -> bool:
        """
        Check if the given maintenance time is allowed given Modobio's policies:
        - For maintenance between the hours of 6am and 11pm, their must be more
        than 14 days of notice
        - For maintenance between the hours of 11pm and 6am, their must be more
        than 2 days of notice
        """
        # Set timezone
        zone = pytz.timezone(current_app.config['MAINTENANCE_TIMEZONE'])
        # Get and set relevant times, force timezone info
        start = datetime.fromisoformat(request.json['start_time']).replace(tzinfo=zone)
        end = datetime.fromisoformat(request.json['end_time']).replace(tzinfo=zone)
        now = datetime.now(tz=zone)

        # Current date but with the time set to the start times of business / overnight
        business_start = datetime.combine(now, time(hour=6, minute=0, second=0))
        # If you use the same logic as business hours, it checks for a range(23, 6) which is not what we want
        # Probably simpler to just use the basic range(6) below
        # overnight_start = datetime.combine(now, time(hour=23, minute=0, second=0))

        # Time windows
        # 6AM-10:59PM
        business_hours = [*range(business_start.hour, (business_start+timedelta(hours=17)).hour)]
        # 11PM-5:59AM
        overnight_hours = [*range(6)]  # 0:00 - 6:00
        overnight_hours.append(23) # 23:00 - 6:00

        # Time Deltas
        short_notice = timedelta(days=2)
        std_notice = timedelta(days=14)

        # If the start datetime is later than the end datetime (e.g. start = 4am, end = 3am)
        if start > end:
            return False

        # Business hours
        if start.hour in business_hours or end.hour in business_hours:
            return True if start > now + std_notice else False
        # Overnight
        elif start.hour in overnight_hours and end.hour in overnight_hours:
            return True if start > now + short_notice else False
        else:
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

        'start_time' and 'end_time' must be iso formatted, naive datetimes. e.g. 2022-04-23T13:30:00.000000
        """
        if not self.is_maint_time_allowed():
            raise BadRequest('Maintenance time is not allowed')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(current_app.config['MAINTENANCE_DYNAMO_TABLE'])

        # Set timezone
        zone = pytz.timezone(current_app.config['MAINTENANCE_TIMEZONE'])

        # Get the current users token auth info
        user, _ = token_auth.current_user()
        user_id = str(user.user_id)

        data = {
            'block_id': str(uuid.uuid4()),
            'start_time': request.json["start_time"],
            'end_time': request.json["end_time"],
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

        # If it was successful, return the newly created block
        # Returning data since it allows the user to see the block_id that was created without having to perform a subsequent scan request on the database
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
            raise BadRequest(f'AWS returned the following error: {response["ResponseMetadata"]["Message"]}')
