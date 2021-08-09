import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import MoxyAssessment
from .data import trainer_moxy_assessment_data

def test_post_moxy_assessment(test_client):
    payload = trainer_moxy_assessment_data
    # send get request for client info on clientid = 1
    response = test_client.post(
        f'/trainer/assessment/moxy/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['vl_side'] == trainer_moxy_assessment_data['vl_side']

def test_get_moxy_assessment(test_client):
    response = test_client.get(
        f'/trainer/assessment/moxy/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['vl_side'] == trainer_moxy_assessment_data['vl_side']
