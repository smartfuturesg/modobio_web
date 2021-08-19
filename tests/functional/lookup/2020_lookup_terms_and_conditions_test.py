from flask.json import dumps

def test_get_terms_and_conditions(test_client):
    response = test_client.get(
        '/lookup/terms-and-conditions/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['terms_and_conditions'] == 'Terms and Conditions'
