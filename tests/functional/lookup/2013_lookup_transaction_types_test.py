from flask.json import dumps

def test_get_transaction_types(test_client):
    response = test_client.get(
        '/lookup/business/transaction-types/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 3
    assert response.json['items'][0]['category'] == 'Telehealth'
    assert response.json['items'][-1]['name'] == 'Supplements'
