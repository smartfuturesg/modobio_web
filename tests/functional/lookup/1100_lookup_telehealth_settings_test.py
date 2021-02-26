from flask.json import dumps

def test_get_telehealth_settings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for lookup telehealth settings 
    WHEN the '/business/telehealth-settings/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/business/telehealth-settings/',
                                headers=staff_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200