
from flask.json import dumps

from odyssey.api.client.models import ClientMobileSettings

from tests.functional.client.data import clients_mobile_settings

def test_post_client_mobile_settings(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for setting a client's mobile settings
    WHEN the '/client/mobile-settings/<client id>' resource  is requested to be added (POST)
    THEN the response is the client's settings
    """
    
    response = test_client.post("/client/mobile-settings/1/",
                                headers=client_auth_header, 
                                data=dumps(clients_mobile_settings), 
                                content_type='application/json')
    
    assert response.status_code == 201
    assert response.json.get('general_settings')['date_format'] == clients_mobile_settings['general_settings']['date_format']

def test_get_client_mobile_settings(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for getting mobile settings of a client
    WHEN the '/client/mobile-settings/<client id>' resource is requested (GET)
    THEN the the list of settings is returned
    """

    response = test_client.get("/client/mobile-settings/1/",
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

def test_put_client_mobile_settings(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point updating a client's mobile settings
    WHEN the '/client/mobile-settings/<client id>' resource  is requested to be updated (PUT)
    THEN the response will be 201
    """
    clients_mobile_settings['general_settings']['is_right_handed'] = False

    response = test_client.put("/client/mobile-settings/1/",
                                data=dumps(clients_mobile_settings),
                                headers=client_auth_header, 
                                content_type='application/json')
    
    
    client_settings  = ClientMobileSettings.query.filter_by(user_id = 1).one_or_none()
    
    assert response.status_code == 201
    assert response.json.get('general_settings')['date_format'] == clients_mobile_settings['general_settings']['date_format']

    #test request with invalid date format
    clients_mobile_settings['general_settings']['date_format'] = 'notadateformat'

    response = test_client.put("/client/mobile-settings/1/",
                                data=dumps(clients_mobile_settings),
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 400