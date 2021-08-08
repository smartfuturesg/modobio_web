from odyssey.api.user.models import User, UserLogin

def test_get_registration_status(test_client):
    response = test_client.get(
        f'/client/registrationstatus/{test_client.client_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200

    # Since this checks the registration status at the end of all of
    # the unit tests, it produces an empty list, indicating
    # the client is up to speed with paperwork.

    if response.json['outstanding'] == []:
        # This assert will pass after tests 3000-3016 pass
        assert response.json['outstanding'] == []
