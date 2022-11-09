
from odyssey.api.lookup.models import LookupRoles
from odyssey.api.provider.models import ProviderRoleRequests
from odyssey.api.user.models import User

def test_provider_role_request(test_client, client_user):
    """
     Make a role request from a client context (POST)
     Request to view all role requests (GET)
     Move role request to inactive status (PUT)
     
    """
    
    role_id = LookupRoles.query.filter_by(role_name='trainer').first().idx

    response = test_client.post(
        f'/provider/role/requests/{client_user["user"].user_id}/?role_id={role_id}',
        headers=client_user["auth_header"],
        content_type='application/json')
    
    user = User.query.filter_by(user_id=client_user["user"].user_id).first()
    role_request = ProviderRoleRequests.query.filter_by(user_id=client_user["user"].user_id).first()

    assert response.status_code == 201
    assert user.is_provider 
    assert role_request.status == 'pending'


    ##
    # get request for provider role request
    ##
    response = test_client.get(
        f'/provider/role/requests/{client_user["user"].user_id}/',
        headers=client_user["auth_header"],
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['items'][0]["status"] == 'pending'

    role_request_id = response.json['items'][0]["idx"]
    ##
    # change status of provider role request to inactive
    ##

    response = test_client.put(
        f'/provider/role/requests/{client_user["user"].user_id}/?request_id={role_request_id}',
        headers=client_user["auth_header"],
        content_type='application/json')

    role_request = ProviderRoleRequests.query.filter_by(user_id=client_user["user"].user_id).first()

    assert response.status_code == 200
    assert role_request.status == 'inactive'

    # delete role request
    ProviderRoleRequests.query.filter_by(user_id=client_user["user"].user_id).delete()


def test_provider_role_request_bad(test_client, client_user):
    """
    request a role that is not considered a provider role
    """
    role_id = LookupRoles.query.filter_by(role_name='client_services').first().idx

    response = test_client.post(
        f'/provider/role/requests/{client_user["user"].user_id}/?role_id={role_id}',
        headers=client_user["auth_header"],
        content_type='application/json')
    
    
    assert response.status_code == 400