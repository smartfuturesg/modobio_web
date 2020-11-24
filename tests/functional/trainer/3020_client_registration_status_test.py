from odyssey.api.user.models import User, UserLogin

def test_get_registration_status(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for client registrations status
    WHEN the '/client/registrationstatus/1' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/registrationstatus/1/',
                                headers=staff_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200

    # Since this checks the registration status at the end of all of
    # the unit tests, it produces an empty list, indicating
    # the client is up to speed with paperwork.

    #if we already ran tests 3000-3016
    if response.json['outstanding'] == []:
        """This assert will pass after tests 3000-3016 pass"""
        assert response.json['outstanding'] == []
    