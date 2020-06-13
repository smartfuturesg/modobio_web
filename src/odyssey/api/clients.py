
from flask import request

from odyssey.models.intake import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract
)
from odyssey.api import bp
from odyssey.api.auth import token_auth

@bp.route('/clients/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_client(client_id):
    """returns client info table as a json for the client_id specified"""
    return ClientInfo.query.filter_by(clientid=client_id).first_or_404().to_dict()

@bp.route('/clientsearch', methods=['GET'])
@token_auth.login_required
def get_clients():
    """returns list of all clients"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                        page=page,per_page=per_page, endpoint='api.get_clients')

    return data

@bp.route('/client/consent/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_client_consent(client_id):
    """returns client info table as a json for the client_id specified"""
    return  ClientConsent.query.filter_by(clientid=client_id).first_or_404().to_dict()

@bp.route('/client/release/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_client_release(client_id):
    """returns client release table as a json for the client_id specified"""
    return  ClientRelease.query.filter_by(clientid=client_id).first_or_404().to_dict()

@bp.route('/client/policies/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_client_policies(client_id):
    """returns client policies table as a json for the client_id specified"""
    return  ClientPolicies.query.filter_by(clientid=client_id).first_or_404().to_dict()

@bp.route('/client/consultcontract/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_client_consult_contract(client_id):
    """returns client consultation table as a json for the client_id specified"""
    return  ClientConsultContract.query.filter_by(clientid=client_id).first_or_404().to_dict()

@bp.route('/client/subscriptioncontract/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_client_subscription_contract(client_id):
    """returns client subscription contract table as a json for the client_id specified"""
    return  ClientSubscriptionContract.query.filter_by(clientid=client_id).first_or_404().to_dict()

@bp.route('/client/individualcontract/<int:client_id>', methods=['GET'])
@token_auth.login_required
def get_client_individual_contract(client_id):
    """returns client info table as a json for the client_id specified"""
    return  ClientIndividualContract.query.filter_by(clientid=client_id).first_or_404().to_dict()


# @bp.route('/client/new', methods=['POST']):
# def register_new_client():
#     "register a new client"
#     client =