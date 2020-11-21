import pathlib

from odyssey.api.user.models import User, UserLogin

def test_get_medical_conditions(test_client, init_database):
    """
    GIVEN an api end point for image upload
    WHEN the  '/doctor/images/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'} 

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/medicalconditions/', headers=headers)

    assert response.status_code == 200
    assert response.json['Autoimmune']['Diabetes type 1'] == 1
    assert response.json['Autoimmune']['Thyroid']['Graves'] == 4