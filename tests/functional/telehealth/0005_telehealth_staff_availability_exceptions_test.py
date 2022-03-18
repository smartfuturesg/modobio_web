from flask.json import dumps


from tests.utils import login

def test_post_staff_availability_exception(test_client):


        response = test_client.post(
            f'/telehealth/settings/staff/availability/exceptions/{test_client.staff_id}/',
            headers=test_client.staff_auth_header,
            data=dumps(availability),
            content_type='application/json')

        assert response.status_code == 201

def test_get_staff_availability_exception(test_client):

    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(queue_data),
        content_type='application/json')

def test_delete_staff_availability_exception(test_client):

    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_queue_client_3_data),
        content_type='application/json')

    assert response.status_code == 201

def test_client_time_select(test_client):
    response = test_client.get(
        f'/telehealth/client/time-select/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['total_options'] == 30