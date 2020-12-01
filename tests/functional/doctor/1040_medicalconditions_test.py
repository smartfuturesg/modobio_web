import pathlib

from odyssey.api.user.models import User, UserLogin

def test_get_medical_conditions(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for image upload
    WHEN the  '/doctor/images/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/medicalconditions/', headers=staff_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 276
    assert len(response.json['items']) == 276