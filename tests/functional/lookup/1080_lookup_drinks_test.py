from flask.json import dumps

def test_get_lookup_drinks(test_client):
    # send get request for drinks lookup table
    response = test_client.get(
        '/lookup/drinks/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_get_lookup_drink_ingredients(test_client):
    # send get request for drink ingredients on drink_id=1
    response = test_client.get(
        '/lookup/drinks/ingredients/1/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
