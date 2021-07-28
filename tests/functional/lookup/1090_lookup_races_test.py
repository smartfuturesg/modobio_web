from flask.json import dumps

def test_get_lookup_races(test_client):
    # send get request for drinks lookup table
    response = test_client.get(
        '/lookup/races/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
