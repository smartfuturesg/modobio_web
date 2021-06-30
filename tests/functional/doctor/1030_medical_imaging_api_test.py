from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.doctor.models import MedicalImaging
from .data import doctor_medical_imaging_data

def test_post_medical_imaging(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for image upload
    WHEN the '/doctor/images/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    
    payload = doctor_medical_imaging_data

    # send get request for client info on user_id = 1
            
    response = test_client.post('/doctor/images/1/', 
                            headers=staff_auth_header, 
                            data = payload)
    
    data = MedicalImaging.query.filter_by(user_id=1).first()

    assert response.status_code == 201
    assert data.image_path
    assert data.image_origin_location == payload['image_origin_location']
    assert data.image_type == payload['image_type']
    assert data.image_read == payload['image_read']

def test_post_medical_imaging_no_image(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for image data upload, no image
    WHEN the '/doctor/images/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data

    
    payload = doctor_medical_imaging_data
    del payload["image"]
    # send get request for client info on user_id = 1
            
    response = test_client.post('/doctor/images/1/', 
                            headers=staff_auth_header, 
                            data = payload)
    
    data = MedicalImaging.query.filter_by(user_id=1).order_by(MedicalImaging.created_at.desc()).first()
    assert response.status_code == 201
    assert data.image_read == payload['image_read']

def test_get_medical_imaging(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for image upload
    WHEN the  '/doctor/images/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data

     

    # send get request for client info on user_id = 1 
    response = test_client.get('/doctor/images/1/', headers=staff_auth_header)
    
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['image_type'] ==  doctor_medical_imaging_data['image_type']
    assert response.json[0]['image_origin_location'] ==  doctor_medical_imaging_data['image_origin_location']
    assert response.json[0]['image_date'] ==  doctor_medical_imaging_data['image_date']
    assert response.json[0]['image_read'] ==  doctor_medical_imaging_data['image_read']
