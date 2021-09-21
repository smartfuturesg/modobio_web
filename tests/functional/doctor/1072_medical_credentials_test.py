from flask.json import dumps

from .data import (
    doctor_credentials_post_1_data,
    doctor_credentials_post_2_data,
    doctor_credentials_post_3_data,
    doctor_credentials_post_4_data,
    doctor_credentials_post_5_data,
    doctor_credentials_put_1_data,
    doctor_credentials_put_2_data,
    doctor_credentials_put_3_data,
    doctor_credentials_put_4_data,
    doctor_credentials_delete_1_data
)

def test_post_1_credentials(test_client):
    response = test_client.post(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_post_1_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_1_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['items']) == 5
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '123456789'
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 2:
                assert cred['credentials'] == '183451435'
            elif cred['state'] == 3:
                assert cred['credentials'] == '123342534'
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
            elif cred['state'] == 3:
                assert cred['credentials'] == '839547692'  
        assert cred['status'] == 'Pending Verification'
          


# Overwrite what was written in POST 1 ##############################
def test_post_2_credentials(test_client):
    response = test_client.post(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_post_2_data),
        content_type='application/json')
    assert response.status_code == 201

def test_get_2_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200    
    assert len(response.json['items']) == 3
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '98714234'
        elif cred['credential_type'] == 'dea':

            assert cred['credentials'] == '43218470'

        else:
            assert cred['credentials'] == '21323512'
  
        assert cred['status'] == 'Pending Verification'
# Overwrite what was written in POST 2, Reset back to POST 1 ##############################
def test_post_3_credentials(test_client):
    response = test_client.post(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_post_1_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_3_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json['items']) == 5
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '123456789'
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 2:
                assert cred['credentials'] == '183451435'
            elif cred['state'] == 3:
                assert cred['credentials'] == '123342534'
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
            elif cred['state'] == 3:
                assert cred['credentials'] == '839547692'  
        assert cred['status'] == 'Pending Verification'      

# Community Manager Verifies Medical Credentials ##############################
# Verifies NPI Number
def test_put_1_credentials(test_client):
    response = test_client.put(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_put_1_data),
        content_type='application/json')

    assert response.status_code == 201    

# Verifies DEA Number
def test_put_2_credentials(test_client):
    response = test_client.put(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_put_2_data),
        content_type='application/json')

    assert response.status_code == 201

# Verifies Medical License Number
def test_put_3_credentials(test_client):
    response = test_client.put(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_put_3_data),
        content_type='application/json')

    assert response.status_code == 201

# Get credentials with updated verification status
def test_get_5_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200 
    assert len(response.json['items']) == 5
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '123456789'
            assert cred['status'] == 'Verified'    
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 2:
                assert cred['credentials'] == '183451435'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '123342534'
                assert cred['status'] == 'Pending Verification' 
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '839547692'
                assert cred['status'] == 'Pending Verification'    

# Overwrite UNverified what was written in POST 3 ##############################
def test_post_4_credentials(test_client):
    response = test_client.post(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_post_3_data),
        content_type='application/json')
    assert response.status_code == 201

def test_get_4_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200 
    assert len(response.json['items']) == 5
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '123456789'
            assert cred['status'] == 'Verified'    
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 2:
                assert cred['credentials'] == '183451435'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '4312079463'
                assert cred['status'] == 'Pending Verification' 
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '85423903'
                assert cred['status'] == 'Pending Verification'

# Overwrite VERIFIED NPI With new number ##############################
def test_post_5_credentials(test_client):
    response = test_client.post(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_post_4_data),
        content_type='application/json')
    assert response.status_code == 201

def test_get_5_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200 
    assert len(response.json['items']) == 5
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '987654321'
            assert cred['status'] == 'Pending Verification'    
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 2:
                assert cred['credentials'] == '183451435'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '4312079463'
                assert cred['status'] == 'Pending Verification' 
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '85423903'
                assert cred['status'] == 'Pending Verification'                      

# Overwrite VERIFIED DEA AZ With new number ##############################
def test_post_5_credentials(test_client):
    response = test_client.post(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_post_5_data),
        content_type='application/json')
    assert response.status_code == 201

def test_get_5_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200 
    assert len(response.json['items']) == 5
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '1296336567'
            assert cred['status'] == 'Pending Verification'    
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 2:
                assert cred['credentials'] == '740329857'
                assert cred['status'] == 'Pending Verification' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '4312079463'
                assert cred['status'] == 'Pending Verification' 
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '85423903'
                assert cred['status'] == 'Pending Verification'     

# DELETE Medical Credentials ##############################
def test_delete_1_credentials(test_client):
    response = test_client.delete(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_delete_1_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_6_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200 
    assert len(response.json['items']) == 4
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '1296336567'
            assert cred['status'] == 'Pending Verification'    
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 3:
                assert cred['credentials'] == '4312079463'
                assert cred['status'] == 'Pending Verification' 
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '85423903'
                assert cred['status'] == 'Pending Verification'      

# Verify NPI number
def test_put_4_credentials(test_client):
    response = test_client.put(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_put_4_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_7_credentials(test_client):
    response = test_client.get(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200 
    assert len(response.json['items']) == 4
    for cred in response.json['items']:
        if cred['credential_type'] == 'npi':
            assert cred['country_id'] == 1
            assert cred['state'] == None
            assert cred['credentials'] == '1296336567'
            assert cred['status'] == 'Verified'    
        elif cred['credential_type'] == 'dea':
            if cred['state'] == 3:
                assert cred['credentials'] == '4312079463'
                assert cred['status'] == 'Pending Verification' 
        else:
            if cred['state'] == 2:
                assert cred['credentials'] == '523746512'
                assert cred['status'] == 'Verified' 
            elif cred['state'] == 3:
                assert cred['credentials'] == '85423903'
                assert cred['status'] == 'Pending Verification'                                           