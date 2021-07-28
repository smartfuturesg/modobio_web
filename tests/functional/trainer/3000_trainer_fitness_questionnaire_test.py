import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from .data import trainer_fitness_questionnaire_data


def test_post_fitness_questionnaire(test_client):
    payload = trainer_fitness_questionnaire_data
    # send get request for client info on clientid = 1
    response = test_client.post(
        f'/trainer/questionnaire/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')
    assert response.status_code == 201
    assert response.json['sleep_hours'] == trainer_fitness_questionnaire_data['sleep_hours']
    assert response.json['stress_sources'][0] == trainer_fitness_questionnaire_data['stress_sources'][0]

def test_get_fitness_questionnaire(test_client):
    response = test_client.get(
        f'/trainer/questionnaire/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['sleep_hours'] == '6-8'
    assert response.json['stress_sources'][0] == 'Family'
