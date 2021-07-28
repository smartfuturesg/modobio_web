from flask.json import dumps

def test_post_client_weight(test_client):
    response = test_client.post(
        f'/client/weight/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'weight': 140}),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('weight') == 140

    #try to submit a weight for a client with a different user_id
    response = test_client.post(
        f'/client/weight/2/',
        headers=test_client.client_auth_header,
        data=dumps({'weight': 140}),
        content_type='application/json')

    #clients cannot submit weights for other clients
    assert response.status_code == 401

def test_get_weight_history(test_client):
    response = test_client.get(
        f'/client/weight/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    #try to view weight history for a client with a different user_id
    response = test_client.post(
        f'/client/weight/2/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    #clients cannot view the weight history of other clients
    assert response.status_code == 401

def test_post_client_height(test_client):
    response = test_client.post(
        f'/client/height/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'height': 140}),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('height') == 140

    #try to submit a height for a client with a different user_id
    response = test_client.post(
        '/client/height/2/',
        headers=test_client.client_auth_header,
        data=dumps({'height': 140}),
        content_type='application/json')

    #clients cannot submit heights for other clients
    assert response.status_code == 401

def test_get_height_history(test_client):
    response = test_client.get(
        f'/client/height/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    #try to view height history for a client with a different user_id
    response = test_client.post(
        '/client/height/2/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    #clients cannot view the height history of other clients
    assert response.status_code == 401

def test_post_client_waist_size(test_client):
    response = test_client.post(
        f'/client/waist-size/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'waist_size': 28}),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json.get('waist_size') == 28

    #try to submit a height for a client with a different user_id
    response = test_client.post(
        '/client/waist-size/2/',
        headers=test_client.client_auth_header,
        data=dumps({'waist_size': 28}),
        content_type='application/json')

    #clients cannot submit heights for other clients
    assert response.status_code == 401

def test_get_height_history(test_client):
    response = test_client.get(
        f'/client/waist-size/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    #try to view height history for a client with a different user_id
    response = test_client.post(
        '/client/waist-size/2/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    #clients cannot view the height history of other clients
    assert response.status_code == 401
