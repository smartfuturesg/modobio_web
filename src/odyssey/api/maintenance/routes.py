import json
import logging
from sre_constants import SUCCESS
import time
import pytz
import uuid
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from flask import Response, current_app, request
from flask_accepts import accepts, responds
from pytest import param
from odyssey.api import api
from odyssey.api.maintenance.schemas import MaintenanceBlocksDeleteSchema
from odyssey.api.maintenance.schemas import MaintenanceBlocksCreateSchema
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from decimal import Decimal


logger = logging.getLogger(__name__)


ns = api.namespace(
    'maintenance', description='Endpoints for functions related to maintenance.')


class MaintenanceDB():
    """
    Functions encompassing DynamoDB functionality.
    """
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(
            current_app.config['MAINTENANCE_DYNAMO_TABLE'])

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def get(self) -> json:
        response = self.table.scan()
        return response['Items']

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def post(self):
        """
        Create a new maintenance block using a given start and end time. Append 
        the current user's ID to the block 
        """
        # Get the current users token auth info
        user, _ = token_auth.current_user()
        user_id = str(user.user_id)

        # TODO: Also store version
        # TODO: Applicable to X version
        # NOTE: Not sure if uuid is the best way to do block_id's
        # NOTE: Not sure if casting the epoch time to int to string is the best way
        response = self.table.put_item(
            Item={
                'block_id': str(uuid.uuid4()),
                'start_time': request.json["start_time"],
                'end_time': request.json["end_time"],
                'created_by': user_id,
                'created_at': datetime.now().isoformat(),
                'deleted': "False",
                'updated_by': None,
                'updated_at': None,
                'comments': request.json['comments']
            }
        )

        return response["ResponseMetadata"]["HTTPStatusCode"]

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def delete(self) -> Response:
        """ 
        Set 'Deleted' flag to true for a maintenance block with the given 'start_time'
        """
        # Get the current users token auth info
        user, _ = token_auth.current_user()
        user_id = str(user.user_id)

        # Deletion process
        # Query using the primary index 'block_id'
        # Add a 'Deleted' flag to the block along with update info
        response = self.table.update_item(
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
                ':updated_at': datetime.now().isoformat()
            },
            ReturnValues="UPDATED_NEW"
        )

        # Return the deleted block attributes
        return response['Attributes']

    def is_maint_time_allowed() -> bool:
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

        start = request.json['start_time'].replace(tz=zone)
        end = request.json['end_time'].replace(tz=zone)
        now = datetime.now(tz=zone)

        # Current date but with the time set to the start times of business / overnight
        business_start = datetime.combine(now, time(hour=6, minute=0, second=0))
        # If you use the same logic as business hours, it checks for a range(23, 6) which is not what we want
        # Probably simpler
        overnight_start = datetime.combine(now, time(hour=23, minute=0, second=0))

        # Time windows
        # 6AM-10:59PM
        business_hours = range(business_start.hour, business_start+timedelta(hours=17))
        # 11PM-5:59AM
        overnight_hours = range(6)
        overnight_hours.append(23)

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
            return True if start > datetime.now() + short_notice else False
        else:
            return False


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/', methods=['GET'])
class Base(BaseResource):
    def get(self) -> any:
        return Response(status=200)


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/list/', methods=['GET'])
class DynamoRead(BaseResource):
    def get(self) -> json:
        """
        Read from the DynamoDB table using data from the request.
        """
        # Instantiate the MaintenanceDB class
        obj1 = MaintenanceDB()
        # Store the results of the get func in 'response'
        response = obj1.get()
        return response


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/schedule/', methods=['POST'])
@ns.doc(params={'start_time': 'The start time of the block', 'end_time': 'The end time of the block'})
class DynamoWrite(BaseResource):
    @accepts(schema=MaintenanceBlocksCreateSchema, api=ns)
    def post(self) -> Response:
        """
        Write to the DynamoDB table using data from the request.
        """
        obj1 = MaintenanceDB()
        response = obj1.post()
        return response


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/delete/', methods=['DELETE'])
@ns.doc(params={'block_id': 'The block_id of the block to delete'})
class DynamoDelete(BaseResource):
    @accepts(schema=MaintenanceBlocksDeleteSchema, api=ns)
    def delete(self) -> Response:
        """
        Add the 'Deleted' flag to a maintenance block with a given 'start_time'
        """
        obj1 = MaintenanceDB()
        response = obj1.delete()

        return response
