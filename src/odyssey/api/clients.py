
from flask import request, jsonify
from flask_restx import Resource, Api

from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.serializers import client_info,pagination
from odyssey import db
from odyssey.models.intake import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract
)

ns = api.namespace('client', description='Operations related to clients')


@ns.route('/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class Client(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_info)
    def get(self, client_id):
        """returns client info table as a json for the client_id specified"""
        return jsonify(ClientInfo.query.get_or_404(client_id).to_dict())

    @ns.expect(client_info)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @ns.marshal_with(client_info)
    def put(self, client_id):
        """edit client info"""
        client = ClientInfo.query.filter_by(clientid=client_id).one_or_none()
        data = request.get_json()
        client.from_dict(data)
        db.session.add(client)
        db.session.commit()
        return jsonify(client.to_dict())

@ns.route('/')
class NewClient(Resource):
    """
        create new clients. This is part of the normal flow where clients register on location
    """
    @token_auth.login_required
    @ns.expect(client_info, validate=True)
    @ns.doc(security='apikey')
    @ns.marshal_with(client_info)
    def post(self):
        """create new client"""
        data = request.get_json()
        client = ClientInfo()
        client.from_dict(data)
        #db.session.add(client)
        #db.session.commit
        response = client.to_dict()
        response['__links'] = api.url_for(Client, client_id = 11)
        return response, 201


@ns.route('/clientsearch', methods=['GET'])
@ns.doc(params={'page': 'request page for paginated clients list', 'per_page': 'number of clients per page'})
class Clients(Resource):
    @ns.doc(security='apikey')
    @ns.expect(pagination)
    @token_auth.login_required
    def get(self):
        """returns list of all clients"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        data, resources = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                            page=page,per_page=per_page)
        data['_links']= {
            'self': api.url_for(Clients, page=page, per_page=per_page),
            'next': api.url_for(Clients, page=page + 1, per_page=per_page)
            if resources.has_next else None,
            'prev': api.url_for(Clients, page=page - 1, per_page=per_page)
            if resources.has_prev else None,
        }

        return jsonify(data)

@ns.route('/consent/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class ConsentContract(Resource):
    """client consent forms"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    def get(self, client_id):
        """returns client consent table as a json for the client_id specified"""
        return  jsonify(ClientConsent.query.filter_by(clientid=client_id).first_or_404().to_dict())

@ns.route('/release/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class ReleaseContract(Resource):
    """Client release forms"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    def get(self, client_id):
        """returns client release table as a json for the client_id specified"""
        return  jsonify(ClientRelease.query.filter_by(clientid=client_id).first_or_404().to_dict())

@ns.route('/policies/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class PoliciesContract(Resource):
    """Client policies form"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    def get(self, client_id):
        """returns client policies table as a json for the client_id specified"""
        return  jsonify(ClientPolicies.query.filter_by(clientid=client_id).first_or_404().to_dict())

@ns.route('/consultcontract/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class ConsultConstract(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    def get(self, client_id):
        """returns client consultation table as a json for the client_id specified"""
        return  jsonify(ClientConsultContract.query.filter_by(clientid=client_id).first_or_404().to_dict())


@ns.route('/subscriptioncontract/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class SubscriptionContract(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    def get(self, client_id):
        """returns client subscription contract table as a json for the client_id specified"""
        return  jsonify(ClientSubscriptionContract.query.filter_by(clientid=client_id).first_or_404().to_dict())

@ns.route('/individualcontract/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class IndividualContract(Resource):
    @ns.doc(security='apikey')
    @token_auth.login_required
    def get(self, client_id):
        """returns client info table as a json for the client_id specified"""
        return  jsonify(ClientIndividualContract.query.filter_by(clientid=client_id).first_or_404().to_dict())






