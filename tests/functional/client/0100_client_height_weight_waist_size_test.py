from flask.json import dumps

def test_post_weight(test_client):
    response = test_client.post(
        f'/client/weight/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'weight': 85.5}),
        content_type='application/json')

    assert response.status_code == 201

    # try to submit a weight for a client with a different user_id
    response = test_client.post(
        f'/client/weight/2/',
        headers=test_client.client_auth_header,
        data=dumps({'weight': 85.5}),
        content_type='application/json')

    # clients cannot submit weights for other clients
    assert response.status_code == 401

def test_get_weight(test_client):
    response = test_client.get(
        f'/client/weight/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['weight'] == 85.5

    # try to view weight for a client with a different user_id
    response = test_client.post(
        f'/client/weight/2/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    #clients cannot view the weight of other clients
    assert response.status_code == 401

def test_post_height(test_client):
    response = test_client.post(
        f'/client/height/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'height': 185.2}),
        content_type='application/json')

    assert response.status_code == 201

    # try to submit a height for a client with a different user_id
    response = test_client.post(
        '/client/height/2/',
        headers=test_client.client_auth_header,
        data=dumps({'height': 185.2}),
        content_type='application/json')

    # clients cannot submit heights for other clients
    assert response.status_code == 401

def test_get_height(test_client):
    response = test_client.get(
        f'/client/height/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['height'] == 185.2

    # try to view height for a client with a different user_id
    response = test_client.post(
        '/client/height/2/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    # clients cannot view the height of other clients
    assert response.status_code == 401

def test_post_waist_size(test_client):
    response = test_client.post(
        f'/client/waist-size/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps({'waist_size': 32.6}),
        content_type='application/json')

    assert response.status_code == 201

    # try to submit a waist size for a client with a different user_id
    response = test_client.post(
        '/client/waist-size/2/',
        headers=test_client.client_auth_header,
        data=dumps({'waist_size': 32.6}),
        content_type='application/json')

    # clients cannot submit waist size for other clients
    assert response.status_code == 401

def test_get_waist_size(test_client):
    response = test_client.get(
        f'/client/waist-size/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['waist_size'] == 32.6

    # try to view waist size for a client with a different user_id
    response = test_client.post(
        '/client/waist-size/2/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    # clients cannot view the waist size of other clients
    assert response.status_code == 401
