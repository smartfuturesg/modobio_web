import time
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.auth import token_auth
from odyssey.api import api
from flask import Response, request, current_app
from datetime import datetime
from datetime import timedelta
import json
import boto3
from boto3.dynamodb.conditions import Key
import uuid
import logging
logger = logging.getLogger(__name__)


ns = api.namespace(
    'maintenance', description='Endpoints for functions related to maintenance.')


@ns.route('/methods/')
class MaintenanceApi(BaseResource):

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(
            current_app.config['MAINTENANCE_DYNAMO_TABLE'])

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def get(self) -> Response:
        response = self.table.scan()
        items = response['Items']
        return items

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def post(self, data) -> Response:
        """
        Create a new maintenance block using a given start and end time. Append 
        the current user's ID to the block 
        """
        # Get the current users token auth info
        user, _ = token_auth.current_user()
        # String casting, boto3 defaults the numbers to Decimals
        user_id = str(user.user_id)

        # TODO: Also store version
        # TODO: Applicable to X version
        # NOTE: Not sure if uuid is the best way to do block_id's
        # NOTE: Not sure if casting the epoch time to int to string is the best way
        response = self.table.put_item(
            Item={
                'block_id': str(uuid.uuid4()),
                'start_time': data["start_time"],
                'end_time': data["end_time"],
                'created_by': user_id,
                'created_at': str(int(time.time())),
                'deleted': "False",
                'updated_by': None,
                'updated_at': None
            }
        )
        return response

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def delete(self, data) -> Response:
        """ 
        Set 'Deleted' flag to true for a maintenance block with the given 'start_time'
        """
        # Get the current users token auth info
        user, _ = token_auth.current_user()
        user_id = str(user.user_id)

        filt = data['Filter']

        # Query the table using the global secondary index 'start_timestart_time-end_time-index'
        block = self.table.query(
            IndexName="start_time-end_time-index",
            KeyConditionExpression=Key('start_time').eq(filt['start_time'])
        )

        # If the query didn't return what we're expecting, return an error
        # NOTE: Is 404 right here?
        if block is None or block.get('Items') is None:
            return Response(response=json.dumps({"Status": "No maintenance block found"}),
                            status=400,
                            mimetype='application/json')

        # Get down to the dict of block info
        # e.g. {'Items': [{'block_id': '1234',...}]} -> {'block_id': '1234',...}
        block = block['Items'][0]

        # Deletion process
        # Query using the primary index 'block_id'
        # Add a 'Deleted' flag to the block along with update info
        response = self.table.put_item(
            Item={
                # Unchanged values from Dynamo
                'block_id': block['block_id'],
                'start_time': block['start_time'],
                'end_time': block['end_time'],
                'created_by': block['created_by'],
                'created_at': block['created_at'],
                # New values
                'deleted': "True",
                'updated_by': user_id,
                'updated_at': str(int(time.time()))
            }
        )
        return response


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/')
class Base(BaseResource):
    def get(self) -> Response:
        return Response(response=json.dumps({"Status": "UP"}),
                        status=200,
                        mimetype='application/json')


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/list-blocks', methods=['GET'])
class DynamoRead(BaseResource):
    def get(self) -> Response:
        """
        Read from the DynamoDB table using data from the request.
        """
        # Instantiate the MaintenanceApi class
        obj1 = MaintenanceApi()
        # Store the results of the get func in 'response'
        response = obj1.get()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/schedule-block', methods=['POST'])
class DynamoWrite(BaseResource):
    def post(self) -> Response:
        """
        Write to the DynamoDB table using data from the request.
        """
        data = request.json['Document']

        # If the request doesn't have the relevant info, return an error
        if data is None or data == {} or 'start_time' not in data:
            return Response(response=json.dumps({"Error": "Please provide request information"}),
                            status=400,
                            mimetype='application/json')

        # Made this a var to shorten the if statement
        dts = datetime.fromtimestamp

        # Check if the start and end times are allowed
        if is_maint_time_allowed(dts(int(data['start_time'])), dts(int(data['end_time']))):
            obj1 = MaintenanceApi(data)
            response = obj1.post(data)
            return Response(response=json.dumps(response),
                            status=200,
                            mimetype='application/json')
        # If the times are not allowed, return an error
        else:
            return Response(response=json.dumps({"Error": "Maintenance time is not allowed"}),
                            status=400,
                            mimetype='application/json')


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/delete-block', methods=['DELETE'])
class DynamoDelete(BaseResource):
    def delete(self) -> Response:
        """
        Add the 'Deleted' flag to a maintenance block with a given 'start_time'
        """
        data = request.json

        if data is None or data == {} or 'Filter' not in data:
            return Response(response=json.dumps({"Error": "Please provide request information"}),
                            status=400,
                            mimetype='application/json')

        obj1 = MaintenanceApi(data)
        response = obj1.delete(data)

        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


def is_maint_time_allowed(start: datetime, end: datetime) -> bool:
    """
    Check if the given maintenance time is allowed given Modobio's policies:
        - For maintenance between the hours of 6am and 11pm, their must be more 
        than 14 days of notice
        - For maintenance between the hours of 11pm and 6am, their must be more 
        than 2 days of notice 
    """
    # Time Deltas
    short_notice = timedelta(days=2)
    std_notice = timedelta(days=14)

    # If the start time is later than the end time (e.g. start = 4am, end = 3am)
    if start > end:
        return False

    # Business hours
    if start.hour in range(6, 22) or end.hour in range(6, 22):
        return True if start > datetime.now() + std_notice else False
    # Overnight
    elif (start.hour in range(23, 24) or start.hour in range(0, 5)) and (end.hour in range(23, 24) or end.hour in range(0, 5)):
        return True if start > datetime.now() + short_notice else False
    else:
        return False
