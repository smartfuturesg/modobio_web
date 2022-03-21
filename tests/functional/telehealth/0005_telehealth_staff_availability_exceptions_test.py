from flask.json import dumps


from tests.utils import login
from .data import telehealth_exceptions_post_data

def test_post_staff_availability_exception(test_client):
    response = test_client.post(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_exceptions_post_data),
        content_type='application/json')

    assert response.status_code == 201
    assert response.data[0]['exception_booking_window_id_start_time'] == 120
    assert response.data[0]['exception_booking_window_id_end_time'] == 150
    assert response.data[0]['exception_date'] == "2030-01-01"

def test_get_staff_availability_exception(test_client):

    response = test_client.get(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.staff_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')
    
    assert response.status_code == 200
    assert response.data[0]['exception_booking_window_id_start_time'] == 120
    assert response.data[0]['exception_booking_window_id_end_time'] == 150
    assert response.data[0]['exception_date'] == "2030-01-01"
    

def test_delete_staff_availability_exception(test_client):

    response = test_client.post(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.staff_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'exception_id': 1}),
        content_type='application/json')

    assert response.status_code == 204
    
    response = test_client.get(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.staff_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')
    
    assert response.status_code == 200
    assert response.data == []
