from flask.json import dumps

from odyssey.api.doctor.models import MedicalImaging
from .data import doctor_medical_imaging_data

def test_post_medical_imaging(test_client):
    payload = doctor_medical_imaging_data

    response = test_client.post(
        f'/doctor/images/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=payload)

    data = MedicalImaging.query.filter_by(user_id=test_client.client_id).first()

    assert response.status_code == 201
    assert data.image_path
    assert data.image_origin_location == payload['image_origin_location']
    assert data.image_type == payload['image_type']
    assert data.image_read == payload['image_read']

def test_post_medical_imaging_no_image(test_client):
    payload = doctor_medical_imaging_data
    del payload['image']

    response = test_client.post(
        f'/doctor/images/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=payload)

    data = (MedicalImaging
        .query
        .filter_by(user_id=test_client.client_id)
        .order_by(MedicalImaging.created_at.desc())
        .first())

    assert response.status_code == 201
    assert data.image_read == payload['image_read']

def test_get_medical_imaging(test_client):
    response = test_client.get(
        f'/doctor/images/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['image_type'] ==  doctor_medical_imaging_data['image_type']
    assert response.json[0]['image_origin_location'] ==  doctor_medical_imaging_data['image_origin_location']
    assert response.json[0]['image_date'] ==  doctor_medical_imaging_data['image_date']
    assert response.json[0]['image_read'] ==  doctor_medical_imaging_data['image_read']

def test_delete_medical_imaging(test_client):
    response = test_client.delete(
        f'/doctor/images/{test_client.client_id}/?image_id=1',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 204

    response = test_client.get(
        f'/doctor/images/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 1