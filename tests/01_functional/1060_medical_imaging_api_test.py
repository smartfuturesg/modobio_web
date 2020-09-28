import time , pathlib, os
from datetime import datetime

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.doctor import MedicalImaging
from tests.data import test_medical_imaging


def test_post_medical_imaging(test_client, init_database):
    """
    GIVEN an api end point for image upload
    WHEN the '/doctor/images/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    payload = test_medical_imaging

    # send get request for client info on clientid = 1
            
    response = test_client.post('/doctor/images/1/', 
                            headers=headers, 
                            data = payload)
      
    assert response.status_code == 201
    data = MedicalImaging.query.filter_by(clientid=1).first()
    assert data.image_path
    assert pathlib.Path(data.image_path).exists() 
    assert data.image_date == datetime.fromisoformat(payload['image_date'])
    assert data.image_origin_location == payload['image_origin_location']
    assert data.image_type == payload['image_type']
    assert data.image_read == payload['image_read']



def test_get_medical_imaging(test_client, init_database):
    """
    GIVEN an api end point for image upload
    WHEN the  '/doctor/images/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'} 

    # send get request for client info on clientid = 1 
    response = test_client.get('/doctor/images/1/', headers=headers)
    
    #breakpoint()
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['image_type'] ==  test_medical_imaging['image_type']
    assert response.json[0]['image_origin_location'] ==  test_medical_imaging['image_origin_location']
    assert response.json[0]['image_date'] ==  test_medical_imaging['image_date']
    assert response.json[0]['image_read'] ==  test_medical_imaging['image_read']