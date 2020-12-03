import pathlib

from flask.json import dumps

from odyssey.api.user.models import User
from odyssey.api.doctor.models import MedicalSurgeries
from odyssey.api.staff.models import StaffProfile
from .data import doctor_surgery_data

def test_post_surgery(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for image upload
    WHEN the '/doctor/images/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    
    payload = doctor_surgery_data

    client_user_id = User.query.filter_by(is_client=True).first().user_id
    response = test_client.post('/doctor/surgery/' + str(client_user_id) +'/', 
                            headers=staff_auth_header, 
                            data = dumps(payload),
                            content_type='application/json')
    
    data = MedicalSurgeries.query.filter_by(client_user_id=client_user_id).first()
    assert response.status_code == 201
    assert data.institution == payload['institution']
    assert data.surgery_category == payload['surgery_category']

    #test with invalid sugery_category
    payload['surgery_category'] = "Nonsense garbage category"

    response = test_client.post('/doctor/surgery/' + str(client_user_id) +'/', 
                        headers=staff_auth_header, 
                        data = dumps(payload),
                        content_type='application/json')
                    
    #should get 400 bad request
    assert response.status_code == 400

def test_get_surgery(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point get client surgeries
    WHEN the '/doctor/surgery/' resource  is requested (GET)
    THEN check the response is valid
    """

    # send get request for client info on client_user_id = 1        
    response = test_client.get('/doctor/surgery/1/', 
                            headers=staff_auth_header, 
                            content_type='application/json')
    
    data = MedicalSurgeries.query.filter_by(client_user_id=1).first()
    assert response.status_code == 200
    assert data.institution == "Our Lady of Perpetual Surgery"
    assert data.surgery_category == "Heart"