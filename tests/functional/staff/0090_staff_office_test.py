from flask import current_app
from .data import staff_office_data
from flask.json import dumps

def test_post_staff_office(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for storing data about a professional's office
    WHEN the '/staff/office/' resource is requested (POST)
    THEN check that the office data is stored
    """

    #test with invalid country id, should return 404
    response = test_client.post('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['invalid_country_id']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 404

    #test with a field that exceeds its maximum length, should return 400
    response = test_client.post('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['too_long']),
                                content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 400

    #test with invalid country id, should return 404
    response = test_client.post('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['invalid_phone_type']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with valid data, should return 201
    response = test_client.post('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['normal_data']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['country'] == 'USA'
    assert response.json['city'] == 'Phoenix'
    assert response.json['phone'] == '1234567'

def test_get_staff_office(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for viewing a staff's office
    WHEN the '/staff/office/' resource is requested (GET)
    THEN check that the response is valid
    """

    response = test_client.get('/staff/offices/2/',
                                headers=staff_auth_header)
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['country'] == 'USA'
    assert response.json['phone'] == '1234567'

def test_put_staff_profile(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for updating data about a professional's office
    WHEN the '/staff/office/' resource is requested (PUT)
    THEN check that the office data is updated
    """

    #test with invalid country id, should return 404
    response = test_client.put('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['invalid_country_id']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 404

    #test with a field that exceeds its maximum length, should return 400
    response = test_client.put('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['too_long']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with invalid country id, should return 404
    response = test_client.put('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['invalid_phone_type']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with valid data, should return 201
    response = test_client.put('/staff/offices/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_office_data['normal_data_2']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['country'] == 'USA'
    assert response.json['city'] == 'Tucson'
    assert response.json['phone'] == '1234560'