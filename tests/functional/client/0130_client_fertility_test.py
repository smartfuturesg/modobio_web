from flask.json import dumps
from odyssey.api.user.models import User
from tests.functional.user.data import users_new_user_client_data
from .data import client_fertility
from ...utils import login

def test_create_female_client(test_client):
    #create new client user where biological_sex_male is False and ensure an entry is made in fertility
    payload = users_new_user_client_data['user_info']
    payload['biological_sex_male'] = False
    payload['email'] = "test_this_user_client_f@modobio.com"
    payload['phone_number'] = "1111111131"    

    # send post request for a new client user account
    response = test_client.post(
        '/user/client/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    assert response.status_code == 201
    
    client = User.query.filter_by(email='test_this_user_client_f@modobio.com').one_or_none()
    client.email_verified = True
    test_client.db.session.flush()
    
    header = login(test_client, client, 'password')

    response = test_client.get(
        f"/client/fertility/{response.json['user_info']['user_id']}/",
        headers=header,
        content_type='application/json')

    assert response.status_code == 200
    test_client.db.session.commit()

def test_post_client_fertility(test_client):    
    #test with mismatching combinations between pregnant and status
    female_user = User.query.filter_by(email="test_this_user_client_f@modobio.com").first()
    header = login(test_client, female_user, 'password')
    
    response = test_client.post(
        f'/client/fertility/{female_user.user_id}/',
        headers=header,
        data=dumps(client_fertility['invalid_pair_1']),
        content_type='application/json')
    
    #should fail
    assert response.status_code == 400
    
    response = test_client.post(
        f'/client/fertility/{female_user.user_id}/',
        headers=header,
        data=dumps(client_fertility['invalid_pair_2']),
        content_type='application/json')
    
    assert response.status_code == 400
    
    #test with valid data
    response = test_client.post(
        f'/client/fertility/{female_user.user_id}/',
        headers=header,
        data=dumps(client_fertility['valid_pair_1']),
        content_type='application/json')
    
    #should succeed
    assert response.status_code == 201
    assert response.json['pregnant'] == True
    assert response.json['status'] == 'second trimester'
    
    #test with valid data
    response = test_client.post(
        f'/client/fertility/{female_user.user_id}/',
        headers=header,
        data=dumps(client_fertility['valid_pair_2']),
        content_type='application/json')
    
    #should succeed
    assert response.status_code == 201
    assert response.json['pregnant'] == False
    assert response.json['status'] == 'follicular phase'
    
    #test when biological_sex_male = True
    female_user.biological_sex_male = True
    test_client.db.session.flush()
    
    response = test_client.post(
        f'/client/fertility/{female_user.user_id}/',
        headers=header,
        data=dumps(client_fertility['valid_pair_1']),
        content_type='application/json')
    
    #should fail
    assert response.status_code == 400
    
def test_get_client_fertility(test_client):
    
    female_user = User.query.filter_by(email='test_this_user_client_f@modobio.com').one_or_none()
    header = login(test_client, female_user, 'password')

    response = test_client.get(
        f"/client/fertility/{female_user.user_id}/",
        headers=header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json[0]['pregnant'] == False
    assert response.json[0]['status'] == 'unknown'    
    assert response.json[1]['pregnant'] == True
    assert response.json[2]['status'] == 'follicular phase'