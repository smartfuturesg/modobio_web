import pytest
from .data import staff_office_data
from flask.json import dumps

def test_post_staff_office(test_client):
    #test with invalid territory id, should return 400
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_territory_id']),
                                content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 400

    #test with a field that exceeds its maximum length, should return 400
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['too_long']),
                                content_type='application/json')

    # some simple checks for validity
    assert response.status_code == 400

    #test with invalid phone type, should return 404
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_phone_type']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with valid data, should return 201
    response = test_client.post(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['normal_data']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['country'] == 'USA'
    assert response.json['city'] == 'Miami'
    assert response.json['phone'] == '4804389574'
    assert response.json['territory_id'] == 1


def test_get_staff_office(test_client):
    response = test_client.get(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header)
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.json['country'] == 'USA'
    assert response.json['phone'] == '4804389574'


def test_put_staff_profile(test_client):
    #test with invalid country id, should return 400
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_territory_id']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with a field that exceeds its maximum length, should return 400
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['too_long']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with invalid country id, should return 404
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['invalid_phone_type']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 400

    #test with valid data, should return 201
    response = test_client.put(f'/staff/offices/{test_client.staff_id}/',
                                headers=test_client.staff_auth_header,
                                data=dumps(staff_office_data['normal_data_2']),
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['country'] == 'USA'
    assert response.json['city'] == 'Tampa'
    assert response.json['phone'] == '4804389575'
    assert response.json['territory_id'] == 1
