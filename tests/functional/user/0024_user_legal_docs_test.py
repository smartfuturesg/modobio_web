import base64

from flask.json import dumps

from .data import users_legal_docs_data

def test_legal_docs_post_request(test_client):
    response = test_client.post(
        f'/user/legal-docs/{test_client.client_id}/',
        data=dumps(users_legal_docs_data['normal_data_1']),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['doc_id'] == 1
    assert response.json['signed'] == True

    #attempt to post again for the same doc id, should raise IllegalSetting (400)
    response = test_client.post(
        f'/user/legal-docs/{test_client.client_id}/',
        data=dumps(users_legal_docs_data['normal_data_1']),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 400

    #attempt to post with invalid doc id, should raise GenericNotFound (404)
    response = test_client.post(
        f'/user/legal-docs/{test_client.client_id}/',
        data=dumps(users_legal_docs_data['bad_doc_id']),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 404

def test_legal_docs_put_request(test_client):
    response = test_client.put(
        f'/user/legal-docs/{test_client.client_id}/',
        data=dumps(users_legal_docs_data['normal_data_2']),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['doc_id'] == 1
    assert response.json['signed'] == False

    #attempt to put for a doc id that has not yet been POSTed for this client
    #should raise GenericNotFound (404)
    response = test_client.put(
        f'/user/legal-docs/{test_client.client_id}/',
        data=dumps(users_legal_docs_data['normal_data_3']),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 404

    #attempt to put with invalid doc id, should raise GenericNotFound (404)
    response = test_client.post(
        f'/user/legal-docs/{test_client.client_id}/',
        data=dumps(users_legal_docs_data['bad_doc_id']),
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 404

def test_legal_docs_get_request(test_client):
    response = test_client.get(
        f'/user/legal-docs/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
