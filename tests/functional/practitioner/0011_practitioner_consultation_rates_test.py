from flask.json import dumps
from .data import pracitioner_consultation_rate_data

def test_post_practitioner_consultation_rates(test_client):
    response = test_client.post(
        f'/practitioner/consult-rates/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(pracitioner_consultation_rate_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_practitioner_consultation_rates(test_client):
    response = test_client.get(
        f'/practitioner/consult-rates/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    for item in response.json:
        if item['role'] == 'medical_doctor':
            assert item['rate'] == 100