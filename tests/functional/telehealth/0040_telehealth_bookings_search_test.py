


from datetime import timedelta
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthChatRooms


def test_get_booking_by_date_time(test_client, booking_function_scope, provider_telehealth_access):
    # change the timing of the call so that it has already ended

    response = test_client.get(
        f'/telehealth/bookings/?staff_user_id={test_client.provider_id}&target_date={str(booking_function_scope.target_date_utc)}',
        headers=test_client.provider_auth_header,
        content_type='application/json')
    
    booking_dates = [booking['target_date_utc'] for booking in response.json.get('bookings') ]
    assert response.status_code == 200
    assert all([booking_date == str(booking_function_scope.target_date_utc) for booking_date in booking_dates])
    
    response = test_client.get(
        f"/telehealth/bookings/?staff_user_id={test_client.provider_id}&target_date={'1977-05-25'}",
        headers=test_client.provider_auth_header,
        content_type='application/json')

    booking_dates = [booking['target_date_utc'] for booking in response.json.get('bookings') ]
    assert response.status_code == 200
    assert len(booking_dates) == 0
    
def test_get_booking_by_status(test_client, booking_function_scope, provider_telehealth_access):
    # change the timing of the call so that it has already ended

    response = test_client.get(
        f"/telehealth/bookings/?staff_user_id={test_client.provider_id}&status={'Accepted'}",
        headers=test_client.provider_auth_header,
        content_type='application/json')

    booking_statuss = [booking['status_history'][0]['status'] for booking in response.json.get('bookings') ]
    assert response.status_code == 200
    assert all([booking_status == 'Accepted' for booking_status in booking_statuss])

    response = test_client.get(
        f"/telehealth/bookings/?staff_user_id={test_client.provider_id}&status={'Canceled'}",
        headers=test_client.provider_auth_header,
        content_type='application/json')

    booking_statuss = [booking['status_history'][0]['status'] for booking in response.json.get('bookings') ]

    assert response.status_code == 200
    assert all([booking_status == 'Canceled' for booking_status in booking_statuss])

    
    
def test_get_booking_by_order(test_client, booking_function_scope, provider_telehealth_access):
    
    # 
    # create an extra booking based on data from the booking fixture used
    #
    chat_room = TelehealthChatRooms.query.filter_by(booking_id = booking_function_scope.idx).first()

    new_target_date = booking_function_scope.target_date_utc + timedelta(days=1)
    
    new_booking = TelehealthBookings(**{k:v for k,v in booking_function_scope.__dict__.items() if
        k not in  ('_sa_instance_state', 'created_at', 'updated_at', 'idx')})

    new_chatroom = TelehealthChatRooms(**{k:v for k,v in chat_room.__dict__.items() if
        k not in  ('_sa_instance_state', 'created_at', 'updated_at', 'room_id')})

    new_booking.target_date_utc = new_target_date

    test_client.db.session.add(new_booking)
    test_client.db.session.flush()

    new_chatroom.booking_id = new_booking.idx
    test_client.db.session.add(new_chatroom)
    test_client.db.session.commit()

    # order by date ascending
    response = test_client.get(
        f"/telehealth/bookings/?staff_user_id={test_client.provider_id}&order=date_asc",
        headers=test_client.provider_auth_header,
        content_type='application/json')

    bookings_ascending = [booking['target_date_utc'] for booking in response.json.get('bookings')]

    # order by date descending
    response = test_client.get(
        f"/telehealth/bookings/?staff_user_id={test_client.provider_id}&order=date_desc",
        headers=test_client.provider_auth_header,
        content_type='application/json')

    bookings_descending = [booking['target_date_utc'] for booking in response.json.get('bookings')]


    # order by most recent booking
    response = test_client.get(
        f"/telehealth/bookings/?staff_user_id={test_client.provider_id}&order=date_recent",
        headers=test_client.provider_auth_header,
        content_type='application/json')
    
    bookings_recent = [booking['target_date_utc'] for booking in response.json.get('bookings')]
    
    # tear down the extra booking
    for status in new_booking.status_history:
        test_client.db.session.delete(status)
    
    test_client.db.session.delete(new_chatroom)
    test_client.db.session.delete(new_booking)
    test_client.db.session.commit()
  
    assert response.status_code == 200
    assert bookings_ascending == bookings_descending[::-1]
    assert bookings_ascending == bookings_recent




    





