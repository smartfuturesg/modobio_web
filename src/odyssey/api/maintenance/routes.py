from odyssey.utils.base.resources import BaseResource
from odyssey.utils.auth import token_auth
from odyssey.api import api
from flask import Response, request, current_app
from datetime import datetime
from datetime import timedelta
import json
import boto3
import logging
logger = logging.getLogger(__name__)


ns = api.namespace(
    'maintenance', description='Endpoints for functions related to maintenance.')


@ns.route('/methods/')
class MaintenanceApi(BaseResource):

    def __init__(self, data):
        # Get the service resource.
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(
            current_app.config['MAINTENANCE_DYNAMO_TABLE'])
        self.data = data

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def get(self) -> Response:
        """
        FIXME: This wasnt working when I tried using self.table, so in the current state 
        every single function needs its own instance of the Dynamo table which is 
        obviously wrong.
        """
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(
            current_app.config['MAINTENANCE_DYNAMO_TABLE'])

        response = table.scan()
        items = response['Items']
        return items

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def post(self, data) -> Response:
        user, user2 = token_auth.current_user()
        # String casting, otherwise boto3 will convert it to a decimal
        user_id = str(user.user_id)

        # TODO: Also store version
        # TODO: Applicable to X version
        response = self.table.put_item(
            Item={
                'start_time': data["start_time"],
                'end_time': data["end_time"],
                'user_id': user_id
            }
        )
        return response

    @token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
    def delete(self, data) -> Response:
        filt = data['Filter']

        response = self.table.delete_item(
            Key={
                'start_time': filt['start_time']
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

        :return: HTTP status code
        """
        response = MaintenanceApi.get(MaintenanceApi)
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/schedule-block', methods=['POST'])
class DynamoWrite(BaseResource):
    def post(self) -> Response:
        """
        Write to the DynamoDB table using data from the request.

        {"end_time": string, epoch time, 
        "start_time": string, epoch time}

        :return: HTTP status code
        """
        # Make the request JSON into a dictionary
        # Try just sending the request
        data = request.json['Document']
        
        # If the request is empty, return an error
        if data is None or data == {} or 'start_time' not in data:
            return Response(response=json.dumps({"Error": "Please provide request information"}),
                            status=400,
                            mimetype='application/json')

        dts = datetime.fromtimestamp

        if is_maint_time_allowed(datetime.now(), dts(int(data['start_time'])), dts(int(data['end_time']))):
            obj1 = MaintenanceApi(data)
            response = obj1.post(data)
            return Response(response=json.dumps(response),
                            status=200,
                            mimetype='application/json')

        else:
            return Response(response=json.dumps({"Error": "Maintenance time is not allowed"}),
                            status=400,
                            mimetype='application/json')


@token_auth.login_required(user_type=('staff',), staff_role=('system_admin',))
@ns.route('/delete-block', methods=['DELETE'])
class DynamoDelete(BaseResource):
    def delete(self) -> Response:
        """
        Delete an item from the DynamoDB table.
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


def is_maint_time_allowed(now: datetime, start: datetime, end: datetime) -> bool:
    # Time Deltas
    short_notice = timedelta(days=2)
    std_notice = timedelta(days=14)

    # Business hours
    if start.hour in range(6, 22) or end.hour in range(6, 22):
        return True if start > now + std_notice else False
    # Overnight
    elif (start.hour in range(23, 24) or start.hour in range(0, 5)) and (end.hour in range(23, 24) or end.hour in range(0, 5)):
        return True if start > now + short_notice else False
    else:
        return False
