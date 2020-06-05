from odyssey.api import bp

@bp.route('/clients/<int:id>', methods=['GET'])
def get_client(id):
    return {'client': 'tester', 'id': id}


@bp.route('/clients', methods=['GET'])
def get_clients():
    return {'client': 'all clients'}