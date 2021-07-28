import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import StrengthAssessment
from .data import trainer_movement_assessment_data

def test_post_movement_assessment(test_client):
    payload = trainer_movement_assessment_data
    # send get request for client info on clientid = 1
    response = test_client.post(
        f'/trainer/assessment/movement/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['toe_touch']['ribcage_movement'][0] == trainer_movement_assessment_data['toe_touch']['ribcage_movement'][0]

def test_get_movement_assessment(test_client):
    response = test_client.get(
        f'/trainer/assessment/movement/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['toe_touch']['ribcage_movement'][0] == 'Even Bilaterally'
