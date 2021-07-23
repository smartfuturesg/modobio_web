from flask.json import dumps
from .data import pracitioner_affiliation_data

def test_post_practitioner_affiliations(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for adding practitioner organization affiliations
    WHEN the '/practitioner/affiliations/<user_id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # post affiliation to organization with idx 1
    response = test_client.post('/practitioner/affiliations/2/',
                                headers = staff_auth_header,
                                data=dumps(pracitioner_affiliation_data['organization_1']),
                                content_type='application/json')
    assert response.status_code == 201

    # post affiliation to organization with invalid idx 
    response = test_client.post('/practitioner/affiliations/2/',
                                headers = staff_auth_header,
                                data=dumps(pracitioner_affiliation_data['invalid_organization_idx']),
                                content_type='application/json')
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid Organization Index'

    # post affiliation to organization with idx 1 again
    response = test_client.post('/practitioner/affiliations/2/',
                                headers = staff_auth_header,
                                data=dumps(pracitioner_affiliation_data['organization_1']),
                                content_type='application/json')
    assert response.status_code == 400
    assert response.json['message'] == 'Practitioner is already affiliated with organization_idx 1'


    # post affiliation for a client
    response = test_client.post('/practitioner/affiliations/1/',
                                headers = staff_auth_header,
                                data=dumps(pracitioner_affiliation_data['organization_2']),
                                content_type='application/json')
    assert response.status_code == 400
    assert response.json['message'] == 'Not a Practitioner'

    # post affiliation to organization with idx 1
    response = test_client.post('/practitioner/affiliations/2/',
                                headers = staff_auth_header,
                                data=dumps(pracitioner_affiliation_data['organization_2']),
                                content_type='application/json')
    assert response.status_code == 201

def test_get_practitioner_affiliations(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for viewing practitioner organization affiliations
    WHEN the '/practitioner/affiliations/<user_id>' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/practitioner/affiliations/2/',
                                headers = staff_auth_header)
    assert response.status_code == 200
    assert len(response.json) == 2


def test_delte_practitioner_affiliations(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for removing practitioner organization affiliations
    WHEN the '/practitioner/affiliations/<user_id>' resource  is requested (DELETE)
    THEN check the response is valid
    """
    # test deleting affiliation with organization index 'a'
    response = test_client.delete('/practitioner/affiliations/2/?organization_idx=a',
                                headers = staff_auth_header)
    assert response.status_code == 400
    assert response.json['message'] == 'organization_idx must be a positive integer'

    # test deleting affiliation with organization index null
    response = test_client.delete('/practitioner/affiliations/2/?organization_idx=',
                                headers = staff_auth_header)
    assert response.status_code == 400
    assert response.json['message'] == 'organization_idx must be a positive integer'

    # test deleting affiliation with organization index 50
    response = test_client.delete('/practitioner/affiliations/2/?organization_idx=50',
                                headers = staff_auth_header)
    assert response.status_code == 200

    # check nothing has been deleted so far
    response = test_client.get('/practitioner/affiliations/2/',
                                headers = staff_auth_header)
    assert response.status_code == 200
    assert len(response.json) == 2

    # test deleting affiliation with organization index 1
    response = test_client.delete('/practitioner/affiliations/2/?organization_idx=1',
                                headers = staff_auth_header)
    assert response.status_code == 200

    # check only affiliation with organization idx 1 was deleted
    response = test_client.get('/practitioner/affiliations/2/',
                                headers = staff_auth_header)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['organization_idx'] == 2

    # test deleting all affiliations i.e. no param provided
    response = test_client.delete('/practitioner/affiliations/2/',
                                headers = staff_auth_header)
    assert response.status_code == 200

    # check there are no more affiliations for user_id 2
    response = test_client.get('/practitioner/affiliations/2/',
                                headers = staff_auth_header)
    assert response.status_code == 200
    assert response.json == []