

from odyssey.models.intake import ClientInfo
from odyssey.api import bp

@bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """returns client info table as a json for the client_id specified"""
    return ClientInfo.query.get_or_404(client_id).to_dict()

@bp.route('/clientsearch', methods=['GET'])
def get_clients():
    """returns list of all clients"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                        page=page,per_page=per_page, endpoint='api.get_clients')
    
    return data