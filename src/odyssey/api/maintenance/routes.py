import logging
from sqlalchemy import and_

from odyssey.api.maintenance.models import MaintenanceBlocks
logger = logging.getLogger(__name__)

import requests
import json

from pymongo import MongoClient

from flask import Response, request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
from werkzeug.exceptions import BadRequest, Unauthorized
from odyssey import db, mongo
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.misc import check_client_existence
from odyssey.utils.base.resources import BaseResource
# Models
from odyssey.api.lookup.models import LookupOrganizations
from odyssey.api.payment.models import PaymentMethods, PaymentStatus, PaymentHistory, PaymentRefunds
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.user.models import User

ns = api.namespace('maintenance', description='Endpoints for functions related to maintenance.')

@ns.route('/methods/<int:staff_id>/')
class MaintenanceApi(BaseResource):
    # Multiple payment methods per user allowed
    __check_resource__ = False

    def __init__(self, data):
        self.client = MongoClient("mongodb://127.0.0.1:5000/")

        database = data['database']
        collection = data['collection']
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data = data

    #@token_auth.login_required(user_type=('staff',))
    def get(self):
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output
    
    #@token_auth.login_required(user_type=('staff',))
    def put(self, data):
        new_document = data['Document']
        response = self.collection.insert_one(new_document)
        output = {'Status': 'Successfully Inserted', 'Document_ID': str(response.inserted_id)}
        return output

    #@token_auth.login_required(user_type=('staff',))
    def update(self):
        filt = self.data['Filter']
        updated_data = {"$set": self.data['DataToBeUpdated']}
        response = self.collection.update_one(filt, updated_data)
        output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
        return output

    #@token_auth.login_required(user_type=('staff',))
    def delete(self, data):
        filt = data['Document']
        response = self.collection.delete_one(filt)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output


@ns.route('/')
class Base(BaseResource):
    def get(self):
        """
        Base route

        :return: 
        """
        return Response(response=json.dumps({"Status": "UP"}),
                                status=200,
                                mimetype='application/json')


@ns.route('/list-blocks')
class MongoRead(BaseResource):
    def get(self):
        """
        Read from the MongoDB table using data from the request.

        :return: HTTP status code
        """
        data = request.json
        if data is None or data == {}:
            return Response(response=json.dumps({"Error": "Please provide connection information"}),
                            status=400,
                            mimetype='application/json')
        obj1 = MaintenanceApi(data)
        response = obj1.get()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


@ns.route('/schedule-block')
class MongoWrite(BaseResource):
    def put(self):
        """
        Write to the MongoDB table using data from the request.

        :return: HTTP status code
        """
        # Make the request JSON into a dictionary
        data = request.json
        # If the request is empty, return an error
        if data is None or data == {} or 'Document' not in data:
            return Response(response=json.dumps({"Error": "Please provide connection information"}),
                            status=400,
                            mimetype='application/json')


@ns.route('/update-block')
class MongoUpdate(BaseResource):
    def put(self):
        """
        Update an existing item in the MongoDB table.

        :return: HTTP status code
        """
        data = request.json
        if data is None or data == {} or 'Filter' not in data:
            return Response(response=json.dumps({"Error": "Please provide connection information"}),
                            status=400,
                            mimetype='application/json')
        obj1 = MaintenanceApi(data)
        response = obj1.put()
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')


@ns.route('/delete-block')
class MongoDelete(BaseResource):
    def delete(self):
        """
        Delete an item from the MongoDB table.

        :return: HTTP status code
        """
        data = request.json
        if data is None or data == {} or 'Filter' not in data:
            return Response(response=json.dumps({"Error": "Please provide connection information"}),
                            status=400,
                            mimetype='application/json')
        obj1 = MaintenanceApi(data)
        response = obj1.delete(data)
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype='application/json')
