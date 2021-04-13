from flask.json import dumps
from odyssey.api.client.models import ClientTransactionHistory
from .data import clients_transactions

def test_post_client_transactions(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for submitting a client transaction
    WHEN the '/client/transaction/<idx>/' resource  is requested (POST)
    THEN check the response is successful
    """
    response = test_client.post("/client/transaction/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_transactions[0]), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('category') == 'Telehealth'

def test_get_client_transaction_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for getting the transaction history of a client
    WHEN the '/client/transaction/history/<client id>/' resource is requested (GET)
    THEN the transaction history of the client is returned
    """

    response = test_client.get("/client/transaction/history/1/",
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

def test_put_client_transaction(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for updating a client transaction
    WHEN the '/client/transaction/<idx>/' resource  is requested (PUT)
    THEN check the response is successful
    """
    transaction_1 = ClientTransactionHistory.query.filter_by(idx=1).one_or_none()
    transaction_1_name = transaction_1.name
    
    response = test_client.put("/client/transaction/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_transactions[1]), 
                                content_type='application/json')

    # pull up the updated transaction
    transaction_2 = ClientTransactionHistory.query.filter_by(idx=1).one_or_none()
    transaction_2_name = transaction_2.name
    
    assert response.status_code == 201
    assert response.json.get('price') == 89.99
    assert transaction_1_name != transaction_2_name


def test_get_client_transaction(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for getting a transaction
    WHEN the '/client/transaction/<idx>/' resource is requested (GET)
    THEN the transaction is returned
    """

    response = test_client.get("/client/transaction/1/",
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200
    assert response.json.get('name') == "Diagnosis"