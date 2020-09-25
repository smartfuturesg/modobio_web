import time , pathlib, requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from werkzeug.datastructures import FileStorage
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
    headers = {'Authorization': 'Bearer cpSVFlP9g0bNmSVKHtQ9iR2efEt9Q8HM'}#'Authorization': f'Bearer {token}'}
    payload = test_medical_imaging

    # send get request for client info on clientid = 1
    response = requests.post('http://127.0.0.1:5000/doctor/images/1/', headers=headers, files=payload)
    assert response.status_code == 201


def test_get_medical_imaging(test_client, init_database):
    """
    GIVEN an api end point for image upload
    WHEN the  '/doctor/images/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = Staff().query.first()
    token = staff.get_token()
    headers = {'Authorization': 'Bearer cpSVFlP9g0bNmSVKHtQ9iR2efEt9Q8HM'}#'Authorization': f'Bearer {token}'}

    # send get request for client info on clientid = 1 
    response = requests.get('http://127.0.0.1:5000/doctor/images/1/',
                                headers=headers)
                                
    assert response.status_code == 200