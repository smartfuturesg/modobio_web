import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import PowerAssessment
from .data import trainer_medical_physical_data, trainer_power_assessment_data

def test_post_power_assessment(test_client):

    payload = trainer_power_assessment_data
    response = test_client.post(
        f'/trainer/assessment/power/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['lower_watts_per_kg'] == trainer_power_assessment_data['lower_watts_per_kg']
    assert response.json['leg_press']['bilateral']['attempt_1'] == trainer_power_assessment_data['leg_press']['bilateral']['attempt_1']

def test_get_power_assessment(test_client):
    response = test_client.get(
        f'/trainer/assessment/power/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['lower_watts_per_kg'] == 100
    assert response.json[0]['leg_press']['bilateral']['attempt_1'] == 21
