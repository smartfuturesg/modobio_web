import base64

from flask.json import dumps

from .data import users_legal_docs_data

def test_legal_docs_post_request(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a record of a user legal doc
    WHEN the '/user/legal-docs/{user_id}/' resource  is requested (POST)
    THEN check the response is valid
    """

    response = test_client.post('/user/legal-docs/1/', 
            data=dumps(users_legal_docs_data['normal_data_1']),
            headers=staff_auth_header,
            content_type='application/json')

    assert response.status_code == 200
    assert response.json['doc_id'] == 1
    assert response.json['signed'] == True

    #attempt to post again for the same doc id, should raise IllegalSetting (400)
    response = test_client.post('/user/legal-docs/1/', 
        data=dumps(users_legal_docs_data['normal_data_1']), 
        headers=staff_auth_header,
        content_type='application/json')

    assert response.status_code == 400

    #attempt to post with invalid doc id, should raise GenericNotFound (404)
    response = test_client.post('/user/legal-docs/1/', 
        data=dumps(users_legal_docs_data['bad_doc_id']), 
        headers=staff_auth_header,
        content_type='application/json')

    assert response.status_code == 404

def test_legal_docs_put_request(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a record of a user legal doc
    WHEN the '/user/legal-docs/{user_id}/' resource  is requested (PUT)
    THEN check the response is valid
    """

    response = test_client.put('/user/legal-docs/1/', 
            data=dumps(users_legal_docs_data['normal_data_2']), 
            headers=staff_auth_header,
            content_type='application/json')

    assert response.status_code == 200
    assert response.json['doc_id'] == 1
    assert response.json['signed'] == False

    #attempt to put for a doc id that has not yet been POSTed for this client
    #should raise GenericNotFound (404)
    response = test_client.put('/user/legal-docs/1/', 
        data=dumps(users_legal_docs_data['normal_data_3']), 
        headers=staff_auth_header,
        content_type='application/json')

    assert response.status_code == 404

    #attempt to put with invalid doc id, should raise GenericNotFound (404)
    response = test_client.post('/user/legal-docs/1/', 
        data=dumps(users_legal_docs_data['bad_doc_id']), 
        headers=staff_auth_header,
        content_type='application/json')

    assert response.status_code == 404

def test_legal_docs_get_request(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for viewing records of a user legal docs
    WHEN the '/user/legal-docs/{user_id}/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/user/legal-docs/1/', 
        headers=staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200