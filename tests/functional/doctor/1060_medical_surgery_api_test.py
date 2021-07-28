import pathlib

from flask.json import dumps

from odyssey.api.user.models import User
from odyssey.api.doctor.models import MedicalSurgeries
from odyssey.api.staff.models import StaffProfile
from .data import doctor_surgery_data

def test_post_surgery(test_client):
    payload = doctor_surgery_data

    response = test_client.post(
        f'/doctor/surgery/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    data = MedicalSurgeries.query.filter_by(user_id=test_client.client_id).first()

    assert response.status_code == 201
    assert data.institution == payload['institution']
    assert data.surgery_category == payload['surgery_category']

    #test with invalid sugery_category
    payload['surgery_category'] = 'Nonsense garbage category'

    response = test_client.post(
        f'/doctor/surgery/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    #should get 400 bad request
    assert response.status_code == 400

def test_get_surgery(test_client):
    response = test_client.get(
        f'/doctor/surgery/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    data = MedicalSurgeries.query.filter_by(user_id=test_client.client_id).first()

    assert response.status_code == 200
    assert data.institution == 'Our Lady of Perpetual Surgery'
    assert data.surgery_category == 'Heart'
