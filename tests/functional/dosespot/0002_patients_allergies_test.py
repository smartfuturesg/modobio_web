@pytest.mark.skip('Dosespot API down')
def test_get_patient_ds_allergies_as_client(test_client):
    response = test_client.get(f'/dosespot/allergies/{test_client.client_id}/',
                                headers=test_client.client_auth_header)
    assert response.status_code == 200 

@pytest.mark.skip('Dosespot API down')    
def test_get_patient_ds_allergies_as_practitioner(test_client):
    response = test_client.get(f'/dosespot/allergies/{test_client.client_id}/',
                                headers=test_client.staff_auth_header)
    assert response.status_code == 200 
        