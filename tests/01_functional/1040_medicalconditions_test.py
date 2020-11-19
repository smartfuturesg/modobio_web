import pathlib

from odyssey.models.user import User, UserLogin

def test_get_medical_imaging(test_client, init_database):
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