import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.trainer.models import MoxyRipTest
from .data import trainer_moxy_rip_data, trainer_medical_physical_data

def test_post_moxy_rip_assessment(test_client):
    payload = trainer_moxy_rip_data
    # send get request for client info on clientid = 1
    response = test_client.post(
        f'/trainer/assessment/moxyrip/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['vl_side'] == trainer_moxy_rip_data['vl_side']
    assert response.json['performance']['two']['thb'] == trainer_moxy_rip_data['performance']['two']['thb']

def test_get_moxy_rip_assessment(test_client):
    response = test_client.get(
        f'/trainer/assessment/moxyrip/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['performance']['two']['thb'] == 10
