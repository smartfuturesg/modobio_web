from flask.json import dumps

from .data import doctor_blood_pressures_data

def test_post_1_blood_pressure_history(test_client):
    response = test_client.post(
        f'/doctor/bloodpressure/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(doctor_blood_pressures_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_1_blood_pressure_history(test_client):
    response = test_client.get(
        f'/doctor/bloodpressure/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['items']) == 1
    assert response.json['total_items'] == 1

def test_delete_blood_pressure(test_client):
    response = test_client.delete(
        f'/doctor/bloodpressure/{test_client.client_id}/?idx=1',
        headers=test_client.client_auth_header)

    assert response.status_code == 204

    # send get request to ensure the result was deleted
    response = test_client.get(
        f'/doctor/bloodpressure/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['items']) == 0
    assert response.json['total_items'] == 0
