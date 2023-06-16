from flask.json import dumps

from odyssey.api.organizations.models import Organizations
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
    assert response.json['organization_uuid']  # UUID so just check that it exists


def test_create_org_with_existing_name(test_client):
    """ Test that a community manager can NOT create an organization with an existing name. """

    response = test_client.post(
        '/organizations/',
        headers=test_client.staff_auth_header,
        data=dumps(org),
        content_type='application/json')

    assert response.status_code == 400


def test_create_org_with_invalid_owner(test_client):
    """ Test that a community manager can NOT create an organization with an invalid owner. """
    bad_owner_org = org.copy()
    bad_owner_org['owner'] = 0

    response = test_client.post(
        '/organizations/',
        headers=test_client.staff_auth_header,
        data=dumps(bad_owner_org),
        content_type='application/json'
    )

    assert response.status_code == 400


def test_create_org_with_invalid_max_members(test_client):
    """ Test that a community manager can NOT create an organization with an invalid max_members. """
    bad_max_members_org = org.copy()
    bad_max_members_org['max_members'] = 1000000000

    response = test_client.post(
        '/organizations/',
        headers=test_client.staff_auth_header,
        data=dumps(bad_max_members_org),
        content_type='application/json'
    )

    assert response.status_code == 400


def test_create_org_with_invalid_max_admins(test_client):
    """ Test that a community manager can NOT create an organization with an invalid max_admins. """
    bad_max_admins_org = org.copy()
    bad_max_admins_org['max_admins'] = 1000000000

    response = test_client.post(
        '/organizations/',
        headers=test_client.staff_auth_header,
        data=dumps(bad_max_admins_org),
        content_type='application/json'
    )

    assert response.status_code == 400


# def test_add_members_to_org(test_client):
#     """ Test that a community manager can add members to a valid organization. """
#     # Query for the organization_uuid
#     o = Organizations.query.filter_by(name=org['name']).first()
#     org_uuid = o.organization_uuid
#
#     response = test_client.post(
#         '/organizations/members/',
#         headers=test_client.staff_auth_header,
#         data=dumps({
#             'organization_uuid': org_uuid,
#             'members': [0, 17, 1, 2, 3]
#         }),
#         content_type='application/json'
#     )
#
#     assert response.status_code == 201
#     assert response.json['organization_uuid'] == str(org_uuid)
#     assert response.json['added_members'] == [1, 2, 3]
#     assert response.json['invalid_members'] == [0]
#     assert response.json['prior_members'] == [17]
