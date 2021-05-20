from flask.json import dumps
from odyssey import db

from odyssey.api.telehealth.models import (
    TelehealthBookingDetails,
    TelehealthBookings
)

from odyssey.api.user.models import User
from tests.functional.telehealth.data import (
    telehealth_post_booking_details,
    telehealth_put_booking_details
)

#Process for adding telehealth booking details:
#1. create client, create staff
#2. staff adds availability
#3. client requests a booking on a certain date
#4. client confirms a time
#5. booking is created
#6. client or staff involvedcan add booking details 
#   POST(add booking details to booking_id)
#7. client or staff involved can update booking details 
#   PUT(update booking details, provide booking_id and index of details to alter)
#8. client or staff involved can access booking details
#   GET(get all the details for a booking_id)
#9. client or staff involved can delete all booking details 
#   DELETE(delete all details for a booking_id)
#10. delete client and staff created for this purpose

def test_post_booking_details(test_client, init_database, client_auth_header):
    """
    GIVEN an api endpoint for telehealth booking details
    WHEN the '/telehealth/bookings/details/{booking_id}' resource is requested (POST)
    THEN post the provided details to the given booking_id 
    """
    #client_id = 1  /  staff_id = 2
    #using first booking that comes up in query from those created in tests 1-4
    booking = db.session.query(TelehealthBookings).first()
    #The index in TelehealthBookings is the booking_id
    booking_id = booking.idx
    payload = telehealth_post_booking_details
    
    #add booking details as to existing booking_id
    response = test_client.post(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header,  data=payload)
    assert response.status_code == 201

    #add booking details on the same id with POST, should fail
    response = test_client.post(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header,  data=payload)
    assert response.status_code == 400

    #add booking details as staff to existing booking_id, no authorization
    response = test_client.post(f'/telehealth/bookings/details/{booking_id}',  data=payload)
    assert response.status_code == 401

    #add booking details as staff to non-existing booking_id
    invalid_booking_id = 500
    response = test_client.post(f'/telehealth/bookings/details/{invalid_booking_id}', headers=client_auth_header, data=payload)
    assert response.status_code == 204

    #Post empty payload for booking details
    booking = db.session.query(TelehealthBookings).all()[-1]
    payload = telehealth_put_booking_details['nothing_to_change']
    response = test_client.post(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header,  data=payload)
    assert response.status_code == 400

def test_put_booking_details(test_client, init_database, client_auth_header):
    """
    GIVEN an api endpoint for telehealth booking details
    WHEN the '/telehealth/bookings/details/{booking_id}' resource is requested (PUT)
    THEN alter the provided details to the entry with the given index and booking_id 
    """
    #using first booking that comes up in query from those created in tests 1-4
    booking = db.session.query(TelehealthBookings).first()
    #The index in TelehealthBookings is the booking_id
    booking_id = booking.idx

    #To update an entry of booking details, we need the index, 
    #since we've only created one entry up to now, we use idx = 1 in the data 
    payload1 = telehealth_put_booking_details['remove_img_rec']
    payload2 = telehealth_put_booking_details['swap_img_rec']
    payload3 = telehealth_put_booking_details['change_text_only']
    payload4 = telehealth_put_booking_details['nothing_to_change']
    payload5 = telehealth_put_booking_details['empty_booking_details']
    
    #Remove image and recording from booking details
    response = test_client.put(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header, data=payload1)
    assert response.status_code == 200
    #Change image file and recording file from booking details
    response = test_client.put(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header, data=payload2)
    assert response.status_code == 200
    #Leave image and recording intact, change text details
    response = test_client.put(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header, data=payload3)
    assert response.status_code == 200
    #Submit a request without fields, it will raise a 204, no content error
    response = test_client.put(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header, data=payload4)
    assert response.status_code == 204
    #Submit a request to make every field empty
    response = test_client.put(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header, data=payload5)
    assert response.status_code == 200
    #bad booking_id
    invalid_booking_id = 500
    response = test_client.put(f'/telehealth/bookings/details/{invalid_booking_id}', headers=client_auth_header, data=payload2)
    assert response.status_code == 401

def test_get_booking_details(test_client, init_database, client_auth_header):
    """
    GIVEN an api endpoint for telehealth booking details
    WHEN the '/telehealth/bookings/details/{booking_id}' resource is requested (GET)
    THEN return all the details saved with the given booking_id 
    """
    #using first booking that comes up in query from those created in tests 1-4
    booking = db.session.query(TelehealthBookings).first()
    #The index in TelehealthBookings is the booking_id
    booking_id = booking.idx

    #Get booking details for existing booking_id
    response = test_client.get(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header)
    assert response.status_code == 200
    assert response.json['details'] == 'Only changed text details'
    assert response.json['location_id'] == 1
    assert response.json['images']

    #Try getting booking details for booking_id that doens't exist
    invalid_booking_id = 500
    response = test_client.get(
        f'/telehealth/bookings/details/{invalid_booking_id}',
        headers=client_auth_header)
    assert response.status_code == 204

def test_delete_booking_details(test_client, init_database, client_auth_header):
    """
    GIVEN an api endpoint for telehealth booking details
    WHEN the '/telehealth/bookings/details/{booking_id}' resource is requested (DELETE)
    THEN delete all details entries saved with the given booking_id 
    """
    booking = db.session.query(TelehealthBookings).first()
    booking_id = booking.idx
    
    response = test_client.delete(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header)
    assert response.status_code == 204
    
    #check that details are now deleted
    response = test_client.get(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header)
    assert response.status_code == 204

    #try to delete already deleted details
    response = test_client.delete(f'/telehealth/bookings/details/{booking_id}', headers=client_auth_header)
    assert response.status_code == 404

    invalid_booking_id = 500

    response = test_client.delete(
        f'/telehealth/bookings/details/{invalid_booking_id}',
        headers=client_auth_header)
    assert response.status_code == 404
