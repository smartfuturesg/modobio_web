from flask.json import dumps

from odyssey.api.client.models import ClientMobileSettings

from tests.functional.client.data import clients_mobile_settings

def test_post_client_mobile_settings(test_client):

    response = test_client.post(f'/client/mobile-settings/{test_client.client_id}/',
                                headers=test_client.client_auth_header,
                                data=dumps(clients_mobile_settings),
                                content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('general_settings')['date_format'] == clients_mobile_settings['general_settings']['date_format']

def test_get_client_mobile_settings(test_client):

    response = test_client.get(f'/client/mobile-settings/{test_client.client_id}/',
                                headers=test_client.client_auth_header,
                                content_type='application/json')

    assert response.status_code == 200

def test_put_client_mobile_settings(test_client):
    clients_mobile_settings['general_settings']['is_right_handed'] = False

    response = test_client.put(f'/client/mobile-settings/{test_client.client_id}/',
                                data=dumps(clients_mobile_settings),
                                headers=test_client.client_auth_header,
                                content_type='application/json')

    client_settings  = ClientMobileSettings.query.filter_by(user_id = 1).one_or_none()


    assert response.status_code == 200
    assert response.json.get('general_settings')['date_format'] == clients_mobile_settings['general_settings']['date_format']

    #test request with invalid date format
    clients_mobile_settings['general_settings']['date_format'] = 'notadateformat'

    response = test_client.put(f'/client/mobile-settings/{test_client.client_id}/',
                                data=dumps(clients_mobile_settings),
                                headers=test_client.client_auth_header,
                                content_type='application/json')

    assert response.status_code == 400
