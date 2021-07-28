import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import StrengthAssessment
from .data import trainer_strength_assessment_data

def test_post_strength_assessment(test_client):
    payload = trainer_strength_assessment_data
    # send get request for client info on clientid = 1
    response = test_client.post(
        f'/trainer/assessment/strength/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['upper_push']['right']['estimated_10rm'] == trainer_strength_assessment_data['upper_push']['right']['estimated_10rm']

def test_get_strength_assessment(test_client):
    response = test_client.get(
        f'/trainer/assessment/strength/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['upper_push']['right']['estimated_10rm'] == 250
