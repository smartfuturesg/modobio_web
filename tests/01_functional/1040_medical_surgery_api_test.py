import pathlib

from flask.json import dumps

from odyssey.models.user import User, UserLogin
from odyssey.models.client import ClientSurgeries
from odyssey.models.staff import StaffProfile
from tests.data.doctor.doctor_data import doctor_surgery_data

def test_post_surgery(test_client, init_database):
    """
    GIVEN an api end point for image upload
    WHEN the '/doctor/images/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    payload = doctor_surgery_data
    payload['client_user_id'] = User.query.filter_by(is_client=True).first().user_id
    payload['reporter_user_id'] = StaffProfile.query.first().user_id

    response = test_client.post('/doctor/surgery/', 
                            headers=headers, 
                            data = dumps(payload),
                            content_type='application/json')
    
    data = ClientSurgeries.query.filter_by(client_user_id=1).first()
    assert response.status_code == 201
    assert data.institution == payload['institution']
    assert data.surgery_category == payload['surgery_category']

    #test with invalid sugery_category
    payload['surgery_category'] = "Nonsense garbage category"

    response = test_client.post('/doctor/surgery/', 
                        headers=headers, 
                        data = dumps(payload),
                        content_type='application/json')
                    
    #should get 400 bad request
    assert response.status_code == 400

def test_get_surgery(test_client, init_database):
    """
    GIVEN an api end point get client surgeries
    WHEN the '/doctor/surgery/' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on client_user_id = 1        
    response = test_client.get('/doctor/surgery/1/', 
                            headers=headers, 
                            content_type='application/json')
    
    data = ClientSurgeries.query.filter_by(client_user_id=1).first()
    assert response.status_code == 200
    assert data.institution == "Our Lady of Perpetual Surgery"
    assert data.surgery_category == "Heart"