
def test_get_1_client_time_select(test_client, init_database, staff_auth_header):
    """
    GIVEN an api end point for looking client time select
    WHEN the  '/telehealth/client/time-select/<user_id>/' resource  is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/telehealth/client/time-select/1/', headers=staff_auth_header)


    breakpoint()
    assert response.status_code == 201
