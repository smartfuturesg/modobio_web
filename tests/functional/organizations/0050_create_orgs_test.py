from flask.json import dumps

from .data import org


def test_create_org_as_client(test_client):
    """ Test that a client and non-community-manager can NOT create an organization. """

    response = test_client.post(
        '/organizations/',
        headers=test_client.client_auth_header,
        data=dumps(org),
        content_type='application/json')

    assert response.status_code == 401


def test_create_org_as_community_manager(test_client):
    """ Test that a community manager can create an organization. """

    response = test_client.post(
        '/organizations/',
        headers=test_client.staff_auth_header,
        data=dumps(org),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['name'] == org['name']
    assert response.json['max_members'] == org['max_members']
    assert response.json['max_admins'] == org['max_admins']
    assert response.json['owner'] == org['owner']
    assert response.json['admins'] == [org['owner']]
    assert response.json['members'] == [org['owner']]
    assert response.json['id'] == 1
    assert response.json['created_at']
    assert response.json['updated_at']
