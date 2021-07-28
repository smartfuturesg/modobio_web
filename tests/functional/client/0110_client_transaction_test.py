from flask.json import dumps
from odyssey.api.client.models import ClientTransactionHistory
from .data import clients_transactions

def test_post_client_transactions(test_client):
    response = test_client.post(
        f'/client/transaction/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(clients_transactions[0]),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('category') == 'Telehealth'

def test_get_client_transaction_history(test_client):
    response = test_client.get(
        f'/client/transaction/history/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_put_client_transaction(test_client):
    transaction_1 = ClientTransactionHistory.query.filter_by(idx=1).one_or_none()
    transaction_1_name = transaction_1.name

    response = test_client.put(
        f'/client/transaction/1/',
        headers=test_client.client_auth_header,
        data=dumps(clients_transactions[1]),
        content_type='application/json')

    # pull up the updated transaction
    transaction_2 = ClientTransactionHistory.query.filter_by(idx=1).one_or_none()
    transaction_2_name = transaction_2.name

    assert response.status_code == 201
    assert response.json.get('price') == 89.99
    assert transaction_1_name != transaction_2_name

def test_get_client_transaction(test_client):
    response = test_client.get(
        f'/client/transaction/1/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json.get('name') == 'Diagnosis'
