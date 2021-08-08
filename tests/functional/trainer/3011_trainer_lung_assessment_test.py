import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import LungAssessment
from .data import trainer_lung_assessment_data, trainer_medical_physical_data

def test_post_lung_assessment(test_client):
    payload = trainer_lung_assessment_data
    # send get request for client info on clientid = 1
    response = test_client.post(
        f'/trainer/assessment/lungcapacity/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['notes'] == trainer_lung_assessment_data['notes']

def test_get_lung_assessment(test_client):
    response = test_client.get(
        f'/trainer/assessment/lungcapacity/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['notes'] == 'little struggle but overall fine'
