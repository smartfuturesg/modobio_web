from flask.json import dumps

def test_post_client_weight(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for submitting a client weight
    WHEN the '/client/weight/<client id>/' resource  is requested (POST)
    THEN check the response is successful
    """
    
    response = test_client.post("/client/weight/1/",
                                headers=client_auth_header, 
                                data=dumps({'weight': 140}), 
                                content_type='application/json')

    
    assert response.status_code == 201
    assert response.json.get('weight') == 140

    #try to submit a weight for a client with a different user_id
    response = test_client.post("/client/weight/2/",
                                headers=client_auth_header, 
                                data=dumps({'weight': 140}), 
                                content_type='application/json')

    #clients cannot submit weights for other clients
    assert response.status_code == 401

def test_get_weight_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for getting the weight history of a client
    WHEN the '/client/weight/<client id>/' resource is requested (GET)
    THEN the weight history of the client is returned
    """

    response = test_client.get("/client/weight/1/",
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

    #try to view weight history for a client with a different user_id
    response = test_client.post("/client/weight/2/",
                                headers=client_auth_header,  
                                content_type='application/json')

    #clients cannot view the weight history of other clients
    assert response.status_code == 401

def test_post_client_height(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for submitting a client height
    WHEN the '/client/height/<client id>/' resource  is requested (POST)
    THEN check the response is successful
    """
    
    response = test_client.post("/client/height/1/",
                                headers=client_auth_header, 
                                data=dumps({'height': 140}), 
                                content_type='application/json')

    
    assert response.status_code == 201
    assert response.json.get('height') == 140

    #try to submit a height for a client with a different user_id
    response = test_client.post("/client/height/2/",
                                headers=client_auth_header, 
                                data=dumps({'height': 140}), 
                                content_type='application/json')

    #clients cannot submit heights for other clients
    assert response.status_code == 401

def test_get_height_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for getting the height history of a client
    WHEN the '/client/height/<client id>/' resource is requested (GET)
    THEN the height history of the client is returned
    """

    response = test_client.get("/client/height/1/",
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

    #try to view height history for a client with a different user_id
    response = test_client.post("/client/height/2/",
                                headers=client_auth_header,  
                                content_type='application/json')

    #clients cannot view the height history of other clients
    assert response.status_code == 401

def test_post_client_waist_size(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for submitting a client waist size
    WHEN the '/client/waist-size/<client id>/' resource  is requested (POST)
    THEN check the response is successful
    """
    
    response = test_client.post("/client/waist-size/1/",
                                headers=client_auth_header, 
                                data=dumps({'waist_size': 28}), 
                                content_type='application/json')

    print(response.data)
    assert response.status_code == 201
    assert response.json.get('waist_size') == 28

    #try to submit a height for a client with a different user_id
    response = test_client.post("/client/waist-size/2/",
                                headers=client_auth_header, 
                                data=dumps({'waist_size': 28}), 
                                content_type='application/json')

    #clients cannot submit heights for other clients
    assert response.status_code == 401

def test_get_height_history(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for getting the waist size history of a client
    WHEN the '/client/waist-size/<client id>/' resource is requested (GET)
    THEN the waist size history of the client is returned
    """

    response = test_client.get("/client/waist-size/1/",
                                headers=client_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

    #try to view height history for a client with a different user_id
    response = test_client.post("/client/waist-size/2/",
                                headers=client_auth_header,  
                                content_type='application/json')

    #clients cannot view the height history of other clients
    assert response.status_code == 401