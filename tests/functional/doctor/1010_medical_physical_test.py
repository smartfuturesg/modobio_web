from flask.json import dumps

from tests.functional.trainer.data import trainer_medical_physical_data

def test_post_medical_physical(test_client):
    payload = trainer_medical_physical_data

    response = test_client.post(
        f'/doctor/physical/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['vital_weight'] == trainer_medical_physical_data['vital_weight']
    assert response.json['abdominal_hard'] == trainer_medical_physical_data['abdominal_hard']

def test_get_medical_physical(test_client):
    response = test_client.get(
        f'/doctor/physical/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['vital_weight'] == 110.0
    assert response.json[0]['abdominal_hard'] == True
    assert response.json[0]['reporter_lastname'] == test_client.client.lastname
