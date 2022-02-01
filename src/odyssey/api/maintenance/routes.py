import boto3
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.auth import token_auth
from odyssey.api import api
from flask import Response, request, current_app
from datetime import *
from dateutil.relativedelta import *
from datetime import timedelta
import json
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

    @token_auth.login_required(user_type=('system_admin',))
    def get(self):
        response = self.table.scan()
        items = response['Items']
        return items

    @token_auth.login_required(user_type=('system_admin',))
    @ns.doc(params={'data': 'JSON data'})
    def post(self, data):
        maint = data['Document']
        response = self.table.put_item(
            Item={
                'start_time': maint["start_time"],
                'end_time': maint["end_time"]
            }
        )
        return response

    @token_auth.login_required(user_type=('system_admin',))
    def update(self):
        # TODO: Finish this function
        filt = self.data['Filter']

        response = self.update_item(
            Key={
                'start_time': filt['start_time']
            },
            AttributeUpdates={
                'start_time': {
                    'Value': self.data['start_time'],
                    # available options -> DELETE(delete), PUT(set), ADD(increment)
                    'Action': 'PUT'
                },
                'end_time': {
                    'Value': self.data['end_time'],
                    'Action': 'PUT'
                }
            },
            ReturnValues="UPDATED_NEW"  # returns the new updated values
        )
        return response

    @token_auth.login_required(user_type=('system_admin',))
    def delete(self, data):
        filt = data['Filter']

        response = self.table.delete_item(
            Key={
                'start_time': filt['start_time']
            }
        )
        return response


@token_auth.login_required(user_type=('system_admin',))
@ns.route('/')
class Base(BaseResource):
    def get(self):
        return Response(response=json.dumps({"Status": "UP"}),
                        status=200,
                        mimetype='application/json')


@token_auth.login_required(user_type=('system_admin',))
@ns.route('/list-blocks')
class DynamoRead(BaseResource):
    def get(self):
        """
        Read from the DynamoDB table using data from the request.

        :return: HTTP status code
        """
        response = MaintenanceApi.get(MaintenanceApi)
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


@token_auth.login_required(user_type=('system_admin',))
@ns.route('/schedule-block')
class DynamoWrite(BaseResource):
    def post(self):
        """
        Write to the DynamoDB table using data from the request.

        {"end_time": string, epoch time, 
        "start_time": string, epoch time}

        :return: HTTP status code
        """
        # Make the request JSON into a dictionary
        data = request.json
        # If the request is empty, return an error
        if data is None or data == {} or 'Document' not in data:
            return Response(response=json.dumps({"Error": "Please provide request information"}),
                            status=400,
                            mimetype='application/json')

        obj1 = MaintenanceApi(data)
        response = obj1.post(data)

        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


@token_auth.login_required(user_type=('system_admin',))
@ns.route('/update-block')
class DynamoUpdate(BaseResource):
    def update(self):
        """
        Update an existing item in the DynamoDB table.

        :return: HTTP status code
        """
        data = request.json

        if data is None or data == {} or 'Filter' not in data:
            return Response(response=json.dumps({"Error": "Please provide request information"}),
                            status=400,
                            mimetype='application/json')

        obj1 = MaintenanceApi(data)
        response = obj1.put()

        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


@token_auth.login_required(user_type=('system_admin',))
@ns.route('/delete-block')
class DynamoDelete(BaseResource):
    def delete(self):
        """
        Delete an item from the DynamoDB table.

        :return: HTTP status code
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


def is_maint_time_allowed(now_obj, start_obj, end_obj):
    """
    :param now_obj: datetime object
    :param start_obj: datetime object
    :param end_obj: datetime object

    :return: Boolean
    """

    # 1.    0600 < Y < 2300    = 15 days
    # 2.    2300 < Y ; Y > 0600   = 3 days
    # Time windows in UTC
    # 1.    1300 < Y ; Y < 0600     = 15 days
    # 2.    0600 < Y < 1300     = 3 days
    six_am_mst = "06:00:00"
    eleven_pm_mst = "23:00:00"

    # Time Deltas
    short_notice = timedelta(days=2)
    std_notice = timedelta(days=14)

    # Yes, this is a string of numbers in a weird format
    start = start_obj.strftime("%H:%M:%S")
    end = end_obj.strftime("%H:%M:%S")
    now = now_obj.strftime("%H:%M:%S")

    # And yes, python is somehow able to compare them perfectly
    # Don't question it
    # If maintenance is scheduled for business hours
    if six_am_mst <= start <= eleven_pm_mst and end <= eleven_pm_mst:
        return True if start_obj > now_obj + std_notice else False
    # If maintenance is scheduled for non-business hours
    elif eleven_pm_mst <= start or start <= six_am_mst:
        return True if start_obj > now_obj + short_notice else False
