from flask.json import dumps

from .data import system_telehealth_data

def test_get_system_telehealth_settings(test_client):
    #test GET method on client user_id = 1
    response = test_client.get(
        '/system/telehealth-settings/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['booking_notice_window'] == 8

def test_put_system_telehealth_settings(test_client):
    response = test_client.put(
        '/system/telehealth-settings/',
        headers=test_client.staff_auth_header,
        data=dumps(system_telehealth_data),
        content_type='application/json')

    #endpoint is temporarily disabled, check for 403 status code
    assert response.status_code == 403

    #assert response.status_code == 201
    #assert response.get_json()['booking_notice_window'] == 9
