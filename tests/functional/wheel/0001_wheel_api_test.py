from datetime import datetime, timedelta
import random
from dateutil import tz

from odyssey.integrations.wheel import Wheel

def test_clinician_roster_request(test_client):
    """
    Bring up the clinician roster from the sandbox environment

    uses wheel API wrapper class integrations.wheel.Wheel
    """

    wheel = Wheel()

    full_roster = wheel.physician_roster()

    assert len(full_roster) == 4


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


def test_wheel_clinician_booking_request(test_client):
    """
    Test:
    - Make a booking with a wheel clinician
    - immediately following the booking request, cancel the booking
    - To ensure the booking was canceled, make a request to view the practitioner's availability for that time

    client_id: 1
    staff_id: 30
    booking time: 12.31.21 with some randomness 
    TODO: currently sandbox users do not have availability beyond this year
    """

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
        location_id=1)

    external_booking_id, _ = wheel.make_booking_request(staff_user_id = 30, client_user_id = 1, location_id = 1, booking_id = 99, booking_start_time = start_time_utc)
    
    # cancel the booking
    wheel.cancel_booking(external_booking_id)

    # bring up the practitioner's availability after cancelling the booking
    availability_after_booking = wheel.available_timeslots(
        target_time_range=(start_time_utc, start_time_utc + timedelta(hours=1)), 
        clinician_id=wheel_clinician_dict[30],
        location_id=1)


    assert availability_before_booking[start_time_utc.date()][30] == availability_after_booking[start_time_utc.date()][30]