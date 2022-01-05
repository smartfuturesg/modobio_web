import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from .data import trainer_fitness_questionnaire_data


def test_post_fitness_questionnaire(test_client):
    response = test_client.post(
        f'/trainer/questionnaire/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(trainer_fitness_questionnaire_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_fitness_questionnaire(test_client):
    response = test_client.get(
        f'/trainer/questionnaire/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['sleep_hours'] == trainer_fitness_questionnaire_data['sleep_hours']
    assert response.json['stress_sources'][0] == trainer_fitness_questionnaire_data['stress_sources'][0]

def test_put_fitness_questionnaire(test_client):
    # This one does NOT go up to 11.
    trainer_fitness_questionnaire_data['energy_level'] = 11

    response = test_client.put(
        f'/trainer/questionnaire/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(trainer_fitness_questionnaire_data),
        content_type='application/json')

    assert response.status_code == 400

    trainer_fitness_questionnaire_data['energy_level'] = 9

    response = test_client.put(
        f'/trainer/questionnaire/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(trainer_fitness_questionnaire_data),
        content_type='application/json')

    assert response.status_code == 201

    trainer_fitness_questionnaire_data['energy_level'] = 11

    response = test_client.get(
        f'/trainer/questionnaire/{test_client.client_id}/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert response.json['energy_level'] == 9
