import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.physiotherapy.models import Chessboard
from tests.functional.trainer.data import trainer_chessboard_assessment_data

def test_post_chessboard_assessment(test_client):

    # For COVERAGE, raise ContentNotFound error
    response = test_client.get(
        f'/physiotherapy/chessboard/{test_client.client_id}/',
        headers=test_client.provider_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    payload = trainer_chessboard_assessment_data
    response = test_client.post(
        f'/physiotherapy/chessboard/{test_client.client_id}/',
        headers=test_client.provider_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['isa_structure'] == trainer_chessboard_assessment_data['isa_structure']
    assert response.json['hip']['left']['flexion'] == trainer_chessboard_assessment_data['hip']['left']['flexion']

def test_get_chessboard_assessment(test_client):
    response = test_client.get(
        f'/physiotherapy/chessboard/{test_client.client_id}/',
        headers=test_client.provider_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['isa_structure'] == 'Asymmetrical Atypical'
    assert response.json[0]['hip']['left']['flexion'] == 70
