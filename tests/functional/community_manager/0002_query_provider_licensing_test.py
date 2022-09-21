from odyssey.api.practitioner.models import PractitionerCredentials

def test_get_provider_licensing(test_client):
    #Returns all provider licensing
    response = test_client.get(
        f"/community-manager/provider-licensing",
        headers=test_client.staff_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200

def test_get_provider_licensing_status_query_param(test_client):
    #Returns all provider licensing with status of Verified
    response = test_client.get(
        f"/community-manager/provider-licensing?status=Verified",
        headers=test_client.staff_auth_header,
        content_type="application/json",
    )

    for cred in response.json['provider_licenses']:
        assert cred['status'] == 'Verified'

    assert response.status_code == 200

    cred = PractitionerCredentials.query.filter_by(idx=1).one_or_none()
    cred.status = 'Rejected'
    test_client.db.session.commit()

    #Returns all provider licensing with status of Rejected
    response = test_client.get(
        f"/community-manager/provider-licensing?status=Rejected",
        headers=test_client.staff_auth_header,
        content_type="application/json",
    )
    for cred in response.json['provider_licenses']:
        assert cred['status'] == 'Rejected'
    
    assert response.status_code == 200


def test_get_provider_licensing_by_provider_id(test_client):

    #Returns all provider licensing of test_client modobio_id
    response = test_client.get(
        f"/community-manager/provider-licensing?email={test_client.staff.modobio_id}",
        headers=test_client.staff_auth_header,
        content_type="application/json",
    )

    for cred in response.json['provider_licenses']:
        assert cred['modobio_id'] == test_client.staff.modobio_id

    assert response.status_code == 200
