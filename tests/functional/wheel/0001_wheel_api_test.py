import pytest
from datetime import datetime, timedelta
import random
from dateutil import tz
import pytest

import pytest

from odyssey.integrations.wheel import Wheel

@pytest.mark.skip
def test_clinician_roster_request(test_client):
    """
    Bring up the clinician roster from the sandbox environment

    uses wheel API wrapper class integrations.wheel.Wheel
    """

    wheel = Wheel()

    full_roster = wheel.physician_roster()

    assert len(full_roster) == 4

@pytest.mark.skip
def test_wheel_clinician_openings(test_client):
    """
    Test:
    - Use the wheel API wrappper to find the availability of the MD clinicians
    - For date range 12.30.21-12.31.21

    Expected Result:
    There are two test MD clinicians available on the sandbox. This test will check to ensure
    those clinicians have the expected availability for a date in the future. 

    Test clinicians should be availble between 00:00-05:00 and 13:00-23:59 every day

    The wrapper class will convert the response to 5 minute time blocks which reference the LookupBookingTimeIncrements
    table. 
    """

    wheel = Wheel()

    start_time_range = datetime(year=2021, month=12, day=29, hour=23, minute=50, second=0)
    end_time_range = start_time_range + timedelta(hours=24, minutes=20) # accounts for appointment end buffer

    availability = wheel.openings(target_time_range=(start_time_range, end_time_range), location_id=1)
    
    assert 31 in availability[start_time_range.date()]
    assert 30 in availability[start_time_range.date()]
    assert len(availability[start_time_range.date()][31]) == 380
    assert len(availability[start_time_range.date()][30]) == 380

@pytest.mark.skip('Wheel changed their api, will be fixed later')
def test_wheel_clinician_avialability(test_client):
    """
    Test:
    - Use the wheel API wrappper to find the availability of the MD clinicians
    - For date range 12.30.21-12.31.21

    Expected Result:
    There are two test MD clinicians available on the sandbox. This test will check to ensure
    those clinicians have the expected availability for a date in the future. 

    Test clinicians should be availble between 00:00-05:00 and 13:00-23:59 every day

    The wrapper class will convert the response to 5 minute time blocks which reference the LookupBookingTimeIncrements
    table. 
    """

    wheel = Wheel()

    start_time_range = datetime(year=2021, month=12, day=30, hour=0, minute=0, second=0)
    end_time_range = start_time_range + timedelta(hours=24)

    availability = wheel.available_timeslots(target_time_range=(start_time_range, end_time_range), location_id=1)
    
    assert 31 in availability[start_time_range.date()]
    assert 30 in availability[start_time_range.date()]
    assert len(availability[start_time_range.date()][31]) == 380
    assert len(availability[start_time_range.date()][30]) == 380

@pytest.mark.skip('will be updated in a following story')
def test_wheel_clinician_booking_request(test_client):
    """
    Test:
    - Make a booking with a wheel clinician
    - To ensure the booking was canceled, make a request to view the practitioner's availability for that time

    client_id: 1
    staff_id: 30
    booking time: 12.31.21 with some randomness 
    TODO: currently sandbox users do not have availability beyond this year
    """
    global external_booking_id, availability_before_booking, start_time_utc

    wheel = Wheel()

    # booking start time with a little randomness to reduce the chance of collision if the test
    # that cancels this booking fails
    start_time_utc = datetime(
        year=2021, 
        month=12, 
        day=31, 
        hour=random.choice((0,1,2,3,4)), 
        minute=random.choice((0, 20, 40)), 
        second=0,
        microsecond=0,
        tzinfo=tz.UTC)

    wheel_clinician_dict = wheel.clinician_ids()
        
    availability_before_booking = wheel.available_timeslots(
        target_time_range=(start_time_utc, start_time_utc + timedelta(hours=1)), 
        clinician_id=wheel_clinician_dict[30],
        location_id=1)[start_time_utc.date()][30]
    
    external_booking_id, _ = wheel.make_booking_request(staff_user_id = 30, client_user_id = 1, location_id = 1, booking_id = 99, booking_start_time = start_time_utc)
    
    # bring up the practitioner's availability after making the booking
    availability_after_booking = wheel.available_timeslots(
        target_time_range=(start_time_utc, start_time_utc + timedelta(hours=1)), 
        clinician_id=wheel_clinician_dict[30],
        location_id=1)[start_time_utc.date()][30]

    assert availability_before_booking != availability_after_booking


@pytest.mark.skip("this will always fail as we cannot start consultations early")
def test_booking_start(test_client):
    """
    Test:
    - Attempt to send a booking start request to wheel using the wheel wrapper class

    Expected Result:
    Request should return an error as this request is made too far in advance
    """

    wheel = Wheel()
    response = wheel.start_consult(external_booking_id)

@pytest.mark.skip("this will always fail as we cannot complete consultations early")
def test_booking_complete(test_client):
    """
    Test:
    - Attempt to send a booking complete request to wheel using the wheel wrapper class

    Expected Result:
    Request should return an error as this request is made too far in advance
    """

    wheel = Wheel()
    response = wheel.complete_consult(external_booking_id)

@pytest.mark.skip('will be update in a follow-up story')
def test_cancel_wheel_booking(test_client):
    """
    Test:
    - cancel wheel booking made in previous test using wheel wrapper class
    - check practitioner's availability after cancellation

    Result:
    - practitioner has the same booking window available
    """

    wheel = Wheel()

    wheel_clinician_dict = wheel.clinician_ids()

    wheel.cancel_booking(external_booking_id)

    availability_after_cancellation = wheel.available_timeslots(
        target_time_range=(start_time_utc, start_time_utc + timedelta(hours=1)), 
        clinician_id=wheel_clinician_dict[30],
        location_id=1)[start_time_utc.date()][30]

    assert availability_before_booking == availability_after_cancellation
