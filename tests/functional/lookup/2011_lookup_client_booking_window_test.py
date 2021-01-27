from flask.json import dumps

def test_get_client_booking_window(test_client, init_database, client_auth_header):
    """
    GIVEN a api end point for lookup client booking windows
    WHEN the '/business/booking-window/' resource  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/lookup/business/booking-window/',
                                headers=client_auth_header, 
                                content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['total_items'] == 17
    assert response.json['items'][0]['booking_window'] == 8
    assert response.json['items'][-1]['booking_window'] == 24