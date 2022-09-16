from flask.json import dumps
from odyssey.api.practitioner.models import PractitionerCredentials

from .data import (
    practitioner_credentials_post_1_data,
    practitioner_credentials_post_2_data,
    practitioner_credentials_post_3_data,
    practitioner_credentials_put_1_data,
    practitioner_credentials_put_2_data,
    practitioner_credentials_delete_1_data
)
import pytest
@pytest.skip('spotty DoseSpot', allow_module_level=True)

def test_post_1_credentials(test_client):
    response = test_client.post(
        f'/practitioner/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(practitioner_credentials_post_1_data),
        content_type='application/json')

    credentials = PractitionerCredentials.query.filter_by(user_id=test_client.staff_id) \
        .order_by(PractitionerCredentials.idx.desc()).first()

    assert response.status_code == 201
    #status will be set to 'verified' in test and dev enviornments and 'Pending Verification' in production
    assert credentials.status == 'Verified'

def test_get_1_credentials(test_client):
    response = test_client.get(
        f'/practitioner/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    print(response.json['items'])

    assert response.status_code == 200
    assert len(response.json['items']) > 1

def test_put_1_credentials(test_client):

    credentials = PractitionerCredentials.query.filter_by(user_id=test_client.staff_id) \
        .order_by(PractitionerCredentials.idx.desc()).first()
    
    credentials.status = 'Rejected'
    practitioner_credentials_put_1_data["idx"] = credentials.idx

    response = test_client.put(
        f'/practitioner/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(practitioner_credentials_put_1_data),
        content_type='application/json')

    assert response.status_code == 201    
    assert credentials.status == 'Pending Verification'
    assert credentials.want_to_practice == True
    assert credentials.state == "AZ"
    assert credentials.credential_type == "npi"
          

def test_post_2_credentials_bad_payload_with_same_state(test_client):
    response = test_client.post(
        f'/practitioner/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(practitioner_credentials_post_2_data),
        content_type='application/json')

    assert response.status_code == 400

def test_post_2_credentials_bad_payload_with_state_missing_credential_number(test_client):
    response = test_client.post(
        f'/practitioner/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(practitioner_credentials_post_3_data),
        content_type='application/json')

    assert response.status_code == 400

def test_put_2_credentials_invalid_status(test_client):

    credentials = PractitionerCredentials.query.filter_by(user_id=test_client.staff_id) \
        .order_by(PractitionerCredentials.idx.desc()).first()

    practitioner_credentials_put_2_data["idx"] = credentials.idx

    response = test_client.put(
        f'/practitioner/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(practitioner_credentials_put_1_data),
        content_type='application/json')

    assert response.status_code == 400    

def test_delete_1_credentials(test_client):
    credentials = PractitionerCredentials.query.filter_by(user_id=test_client.staff_id) \
        .order_by(PractitionerCredentials.idx.desc()).first()

    practitioner_credentials_delete_1_data["idx"] = credentials.idx

    response = test_client.delete(
        f'/practitioner/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(practitioner_credentials_delete_1_data),
        content_type='application/json')

    assert response.status_code == 201
  