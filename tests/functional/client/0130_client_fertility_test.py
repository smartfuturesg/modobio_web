from flask.json import dumps
from odyssey.api.user.models import User
from tests.functional.user.data import users_new_user_client_data
from .data import client_fertility
from ...utils import login

def create_female_client(test_client):
    #create new client user where biological_sex_male is False and ensure an entry is made in fertility
    payload = users_new_user_client_data['user_info']
    payload['user_info']['biological_sex_male'] = False
    payload['user_info']['email'] = "test_this_user_client_f@modobio.com"
    payload['user_info']['phone_number'] = "1111111131"    

    # send post request for a new client user account
    response = test_client.post(
        '/user/client/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')
    
    assert response.status_code == 200
    
    client = User.query.filter_by(email='test_this_user_client_f@modobio.com').one_or_none()
    header = login(test_client, client, 'password')
    
    response = test_client.get(
        f"/client/fertility/{response.data['user_info']['user_id']}/",
        headers=header,
        content_type='application/json')

    assert response.status_code == 200

def test_post_client_fertility(test_client):    
    #test when biological_sex_male = True
    response = test_client.post(
        f'/client/fertility/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(client_fertility['valid_pair_1']),
        content_type='application/json')
    
    #should fail
    assert response.status_code == 400
    
    #test with mismatching combinations between pregnant and status
    female_user = User.query.filter_by(user_id=response.data[0]['user_id']).first()
    female_user_id = female_user.user_id
    header = login(test_client, female_user, 'password')
    
    response = test_client.post(
        f'/client/fertility/{female_user_id}/',
        headers=header,
        data=dumps(client_fertility['invalid_pair_1']),
        content_type='application/json')
    
    #should fail
    assert response.status_code == 400
    
    response = test_client.post(
        f'/client/fertility/{female_user_id}/',
        headers=header,
        data=dumps(client_fertility['invalid_pair_2']),
        content_type='application/json')
    
    assert response.status_code == 400
    
    #test with valid data
    response = test_client.post(
        f'/client/fertility/{female_user_id}/',
        headers=header,
        data=dumps(client_fertility['valid_pair_1']),
        content_type='application/json')
    
    #should fail
    assert response.status_code == 200
    assert response.data['pregnant'] == True
    assert response.data['status'] == 'second trimester'
    
    #test with valid data
    response = test_client.post(
        f'/client/fertility/{female_user_id}/',
        headers=header,
        data=dumps(client_fertility['valid_pair_2']),
        content_type='application/json')
    
    #should fail
    assert response.status_code == 200
    assert response.data['pregnant'] == False
    assert response.data['status'] == 'follicular phase'
    
def test_get_client_fertility(test_client):
    
    female_user = User.query.filter_by(email='test_this_user_client_f@modobio.com').one_or_none()
    female_user_id = female_user.user_id
    header = login(test_client, female_user, 'password')

    response = test_client.get(
        f"/client/fertility/{female_user_id}/",
        headers=header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['pregnant'] == True
    assert response.data[1]['status'] == 'follicular phase'