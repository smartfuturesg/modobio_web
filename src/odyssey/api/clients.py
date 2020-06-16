
from flask import request, jsonify
from flask_restx import Resource

from odyssey.models.intake import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract
)
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.serializers import pagination


ns = api.namespace('client', description='Operations related to clients')


@ns.route('/<int:client_id>')
@ns.doc(params={'client_id': 'Client ID number'})
class Client(Resource):
    @token_auth.login_required
    @ns.doc(security='apikey')
    def get(self, client_id):
        """returns client info table as a json for the client_id specified"""
        return jsonify(ClientInfo.query.get_or_404(client_id).to_dict())

@ns.route('/clientsearch', methods=['GET'])
class Clients(Resource):
    @ns.doc(security='apikey')
    @ns.expect(pagination)
    @token_auth.login_required
    def get(self):
        """returns list of all clients"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        data = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                            page=page,per_page=per_page, endpoint='api.clients')

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






