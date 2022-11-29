



import json
from odyssey.api.staff.models import StaffRoles


def test_get_provider_role_requests(test_client, provider_role_request):
    """
    Retrieve all provider role requests as a community manager
    """
    response = test_client.get(
        f"/community-manager/provider/role-requests/",
        headers=test_client.staff_auth_header,
    )
    assert response.status_code == 200
    assert len(response.json.get('provider_role_requests')) == 1
    
def test_grant_provider_role_request(test_client, provider_role_request):
    """ Grant a role request and check that role has been assign correctly"""

    response = test_client.put(
        f"/community-manager/provider/role-requests/",
        headers=test_client.staff_auth_header,
        data=json.dumps({"role_request_id": provider_role_request.idx, "status": "granted"}),
        content_type="application/json",
    )

    # bring up StaffRoles entry
    staff_role = StaffRoles.query.filter_by(user_id=provider_role_request.user_id).one_or_none()
    
    test_client.db.session.refresh(provider_role_request)
    
    assert response.status_code == 200
    assert staff_role is not None
    assert staff_role.role == provider_role_request.role_info.role_name
    assert provider_role_request.status == "granted"
    assert provider_role_request.reviewer_user_id == test_client.staff.user_id

    # delete the staff role
    test_client.db.session.delete(staff_role)
    test_client.db.session.commit()

def test_reject_provider_role_request(test_client, provider_role_request):
    """ Reject a role request """

    response = test_client.put(
        f"/community-manager/provider/role-requests/",
        headers=test_client.staff_auth_header,
        data=json.dumps({"role_request_id": provider_role_request.idx, "status": "rejected"}),
        content_type="application/json",
    )

    # bring up StaffRoles entry
    staff_role = StaffRoles.query.filter_by(user_id=provider_role_request.user_id).one_or_none()
    
    test_client.db.session.refresh(provider_role_request)
    
    assert response.status_code == 200
    assert staff_role is None
    assert provider_role_request.status == "rejected"
    assert provider_role_request.reviewer_user_id == test_client.staff.user_id


