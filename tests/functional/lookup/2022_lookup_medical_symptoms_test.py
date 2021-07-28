from flask.json import dumps

def test_get_medical_symptoms(test_client):
    response = test_client.get(
        '/lookup/medical-symptoms/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 27
    assert response.json['items'][0]['name'] == 'Abdominal Pain'
