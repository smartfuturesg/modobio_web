from flask.json import dumps

from .data import system_telehealth_data


def test_get_system_telehealth_settings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for user notifications (GET)
    WHEN the '/user/notification/<user_id>' resource is requested
    THEN check the response is valid
    """

    #test GET method on client user_id = 1
    response = test_client.get('/system/teleheath-settings/',
                                headers=staff_auth_header,
                                content_type='application/json')
    
    # some simple checks for validity
    assert response.status_code == 200
    assert response.get_json()['booking_notice_window'] == 8

def test_put_system_telehealth_settings(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end points for user notifcations
    WHEN the '/user/notification/<notifications_id>' resource is requested (PUT) 
    THEN check the notification is udpated
    """

    response = test_client.put('/system/teleheath-settings/',
                                headers=staff_auth_header,
                                data=dumps(system_telehealth_data), 
                                content_type='application/json')

    assert response.status_code == 201
    assert response.get_json()['booking_notice_window'] == 9