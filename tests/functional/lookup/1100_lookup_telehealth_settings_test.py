from flask.json import dumps

def test_get_telehealth_settings(test_client):
    response = test_client.get(
        '/lookup/business/telehealth-settings/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
