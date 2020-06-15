
from flask import request, jsonify
from flask_restplus import Resource

from odyssey.models.intake import ClientInfo
from odyssey.api import api
from odyssey.api.auth import token_auth


@api.route('/client/<int:client_id>')
@api.doc(params={'client_id': 'Client ID number'})
class Client(Resource):
    @token_auth.login_required
    @api.doc(security='apikey')
    def get(self, client_id):
        """returns client info table as a json for the client_id specified"""
        return jsonify(ClientInfo.query.get_or_404(client_id).to_dict())

@api.route('/clientsearch', methods=['GET'])
class Clients(Resource):
    @api.doc(security='apikey')
    @token_auth.login_required
    def get(self):
        """returns list of all clients"""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        data = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                            page=page,per_page=per_page, endpoint='api.clients')

        return jsonify(data)

# @bp.route('/clients/<int:client_id>', methods=['GET'])
# #@token_auth.login_required
# def get_client(client_id):
#     """returns client info table as a json for the client_id specified"""
#     return ClientInfo.query.get_or_404(client_id).to_dict()
#
# @bp.route('/clientsearch', methods=['GET'])
# @token_auth.login_required
# def get_clients():
#     """returns list of all clients"""
#     page = request.args.get('page', 1, type=int)
#     per_page = min(request.args.get('per_page', 10, type=int), 100)
#     data = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
#                                         page=page,per_page=per_page, endpoint='api.get_clients')
#
#     return data