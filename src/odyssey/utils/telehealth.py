import logging
import random

from datetime import date, datetime, timedelta, time
from typing import Any

from dateutil import tz
from flask import current_app
from sqlalchemy import select
from sqlalchemy.sql.expression import and_, or_
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.lookup.models import LookupBookingTimeIncrements, LookupTerritoriesOfOperations
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.telehealth.models import(
    TelehealthBookingDetails,
    TelehealthChatRooms, 
    TelehealthBookings, 
    TelehealthStaffAvailability, 
    TelehealthBookingStatus)
from odyssey.api.telehealth.schemas import TelehealthBookingStatusSchema
from odyssey.api.user.models import User
from odyssey.api.staff.models import StaffCalendarEvents, StaffRoles
from odyssey.api.payment.models import PaymentHistory
from odyssey.integrations.wheel import Wheel
from odyssey.integrations.twilio import Twilio
from odyssey.utils.constants import (
    DAY_OF_WEEK,
    TELEHEALTH_BOOKING_LEAD_TIME_HRS,
    TELEHEALTH_START_END_BUFFER)
from odyssey.utils.files import FileDownload

logger = logging.getLogger(__name__)

booking_time_increment_length = 0
booking_max_increment_idx = 0

def get_utc_start_day_time(target_date: datetime, client_tz: str) -> tuple:
    # consider if the request is being made less than TELEHEALTH_BOOKING_LEAD_TIME_HRS before the start of the next day
    # if it's thurs 11 pm, we should offer friday 1 am the earliest, not midnight
    localized_target_date = datetime.combine(target_date.date(), time(0, tzinfo=tz.gettz(client_tz)))
    time_now_client_localized = datetime.now(tz.gettz(client_tz)) + timedelta(hours=TELEHEALTH_BOOKING_LEAD_TIME_HRS)
    
    # if request was for a time in the past or current time, use the present time + booking lead time window
    if localized_target_date <= time_now_client_localized:
        localized_target_date = time_now_client_localized
        # round up the minute to the nearest 15 min interval
        if localized_target_date.minute % 15 != 0:
            minutes = 15 - localized_target_date.minute % 15
            localized_target_date = localized_target_date + timedelta(minutes=minutes)
        localized_target_date = localized_target_date.replace(second=0, microsecond=0)

    localized_end = datetime.combine(localized_target_date.date(), time(23,55,00, tzinfo=tz.gettz(client_tz)))
    day_start_utc = localized_target_date.astimezone(tz.UTC)
    start_time_window_utc = LookupBookingTimeIncrements.query.filter_by(start_time=day_start_utc.time()).first()
    day_end_utc = localized_end.astimezone(tz.UTC)
    end_time_window_utc = LookupBookingTimeIncrements.query.filter_by(start_time=day_end_utc.time()).first()

    return (day_start_utc, start_time_window_utc, day_end_utc, end_time_window_utc)


def get_possible_ranges(
    target_date: datetime,
    weekday_start: int,
    start_time_idx: int,
    weekday_end: int,
    end_time_idx: int,
    duration: int) -> dict:
    # Duration is taken from the client queue.
    # we divide it by 5 because our look up tables are in increments of 5 mintues
    # so, this represents the number of time blocks we will need to look at.
    # The subtract 1 is due to the indices having start_time and end_times, so 100 - 103 is 100.start_time to 103.end_time which is
    # the 20 minute duration
    duration_idx_delta = int(duration/5) - 1
    time_blocks = {}
    last_time_idx = 288
    last_possibe_start = 286
    first_time_idx = 1
    # available times in increments of 15 min / 5 min to get the idx
    available_increments = int(15/5)
    if weekday_start != weekday_end:
        # range example ( start_idx - end_idx )
        # end includes the buffer + 1 to make the idx inclusive in the for loop
        for pos_start in range(start_time_idx, last_time_idx - duration_idx_delta - TELEHEALTH_START_END_BUFFER + 1, available_increments):
            # base case: start_time_idx == 1
            if pos_start == 1 and TELEHEALTH_START_END_BUFFER > 0:
                time_blocks[pos_start] = (
                    (target_date - timedelta(days=1), weekday_start - 1, last_time_idx - TELEHEALTH_START_END_BUFFER + 1, last_time_idx), # 5 min buffer
                    (target_date, weekday_start, pos_start , pos_start + duration_idx_delta + TELEHEALTH_START_END_BUFFER)
                )
            else:
                # add day1 times
                time_blocks[pos_start] = (
                    (target_date, weekday_start, pos_start - TELEHEALTH_START_END_BUFFER, pos_start + duration_idx_delta + TELEHEALTH_START_END_BUFFER),
                )

        # add overlapping times can be 283(23:30) 286(23:45) or ealier ones depending on duration.
        # last possible start time in a day is 286(23:45)
        for pos_start in range(last_possibe_start, last_time_idx - duration_idx_delta - TELEHEALTH_START_END_BUFFER - 1, -available_increments):
            time_blocks[pos_start] = (
                (target_date, weekday_start, pos_start - TELEHEALTH_START_END_BUFFER, last_time_idx),
                (target_date + timedelta(days=1), weekday_end, first_time_idx, TELEHEALTH_START_END_BUFFER + duration_idx_delta - (last_time_idx - pos_start))
            )

        for pos_start in range(first_time_idx, end_time_idx - duration_idx_delta - TELEHEALTH_START_END_BUFFER + 1, available_increments): # +1 to make it inclusive
            # base case: start_time_idx == 1
            if pos_start == 1 and TELEHEALTH_START_END_BUFFER > 0:
                time_blocks[pos_start] = (
                    (target_date, weekday_end - 1, last_time_idx - TELEHEALTH_START_END_BUFFER + 1, last_time_idx), # 5 min buffer
                    (target_date + timedelta(days=1), weekday_end, pos_start , pos_start + duration_idx_delta + TELEHEALTH_START_END_BUFFER)
                )
            else:
                # add day2 times
                time_blocks[pos_start] = (
                    (target_date+timedelta(days=1), weekday_end, pos_start - TELEHEALTH_START_END_BUFFER, pos_start + duration_idx_delta + TELEHEALTH_START_END_BUFFER),
                )
    
    else:
        for pos_start in range(start_time_idx, end_time_idx - duration_idx_delta - TELEHEALTH_START_END_BUFFER + 1, available_increments): # +1 to make it inclusive
            # base case: start_time_idx == 1
            if pos_start == 1 and TELEHEALTH_START_END_BUFFER > 0:
                time_blocks[pos_start] = (
                    (target_date-timedelta(days=1), weekday_start - 1, last_time_idx - TELEHEALTH_START_END_BUFFER + 1, last_time_idx), # 5 min buffer
                    (target_date, weekday_start, pos_start , pos_start + duration_idx_delta + TELEHEALTH_START_END_BUFFER)
                )
            else:
                # add day1 times
                time_blocks[pos_start] = (
                    (target_date, weekday_start, pos_start - TELEHEALTH_START_END_BUFFER, pos_start + duration_idx_delta + TELEHEALTH_START_END_BUFFER),
                )
    
    return time_blocks

def get_practitioners_available(time_block, q_request):
    gender = True if q_request.medical_gender == 'm' else False
    date1, day1, day1_start, day1_end = time_block[0]
    date2, day2, day2_start, day2_end = time_block[1] if len(time_block) > 1 else (None,None,None,None)
    location = LookupTerritoriesOfOperations.query.filter_by(idx=q_request.location_id).one_or_none().sub_territory_abbreviation
    duration = q_request.duration
    
    if q_request.profession_type == 'medical_doctor':
        query = db.session.query(TelehealthStaffAvailability.user_id, TelehealthStaffAvailability)\
            .join(PractitionerCredentials, PractitionerCredentials.user_id == TelehealthStaffAvailability.user_id)\
                    .join(StaffRoles, StaffRoles.idx == PractitionerCredentials.role_id) \
                        .join(User, User.user_id == TelehealthStaffAvailability.user_id) \
                            .filter(PractitionerCredentials.role.has(role=q_request.profession_type),
                            PractitionerCredentials.state == location,
                            StaffRoles.consult_rate != None)
    else:
        query = db.session.query(TelehealthStaffAvailability.user_id, TelehealthStaffAvailability)\
            .join(StaffRoles, StaffRoles.role == q_request.profession_type) \
                .join(User, User.user_id == TelehealthStaffAvailability.user_id) \
                    .filter(StaffRoles.consult_rate != None)
    
    # if we need to check for gender
    if q_request.medical_gender != 'np':
        query = query.filter(User.biological_sex_male == gender)
    
    # if there are no overlaps on time block
    if not day2:    
        query = query.filter(TelehealthStaffAvailability.day_of_week == DAY_OF_WEEK[day1],
            TelehealthStaffAvailability.booking_window_id >= day1_start,
            TelehealthStaffAvailability.booking_window_id <= day1_end)

    # if there are overlaps on time block
    if day2:
        query = query.filter(or_(
            and_(TelehealthStaffAvailability.day_of_week == DAY_OF_WEEK[day1],
            TelehealthStaffAvailability.booking_window_id >= day1_start,
            TelehealthStaffAvailability.booking_window_id <= day1_end),
            and_(
            TelehealthStaffAvailability.day_of_week == DAY_OF_WEEK[day2],
            TelehealthStaffAvailability.booking_window_id >= day2_start,
            TelehealthStaffAvailability.booking_window_id <= day2_end)
            )
        )

    # practitioner availablilty as per availability input
    # available = {user_id(practioner): [TelehealthSTaffAvailability objects] }
    available = {}
    for user_id, avail in query.all():
        if user_id not in available:
            available[user_id] = []
        if avail:
            available[user_id].append(avail)
    

    # filtering through scheduled bookings and removing those availabilities occupied by a booking.
    practitioner_ids = set() # set of practitioner's avaialbe user_ids
    bookings_base_query = db.session.query(TelehealthBookings).filter_by(target_date_utc=date1.date())\
        .filter(TelehealthBookings.status !='Canceled')
    for practitioner_user_id in available:
        current_bookings = bookings_base_query.filter_by(staff_user_id=practitioner_user_id)
        
        availability_range = [avail.booking_window_id for avail in available[practitioner_user_id]] # list of booking indicies

        current_bookings = current_bookings.filter(or_(
            TelehealthBookings.booking_window_id_start_time_utc.in_(availability_range),
            TelehealthBookings.booking_window_id_end_time_utc.in_(availability_range)))
        
        if len(available[practitioner_user_id]) == int(duration/5) + (TELEHEALTH_START_END_BUFFER * 2)\
            and not current_bookings.all():
            #practitioner doesn't have a booking with the date1 and any of the times in the range
            practitioner_ids.add(practitioner_user_id)
    
    return practitioner_ids

def calculate_consult_rate(hourly_rate: float, duration: int) -> float:
    hour_in_min = 60.0
    rate = round(float(hourly_rate) * int(duration) / hour_in_min, 2)
    
    return rate

def get_practitioner_details(user_ids: set, profession_type: str, duration: int) -> dict:
    practitioners = db.session.query(User, StaffRoles.consult_rate)\
        .join(StaffRoles, StaffRoles.user_id==User.user_id)\
            .filter(User.user_id.in_(user_ids),
                StaffRoles.role == profession_type,
                StaffRoles.consult_rate != None
            ).all()

    # {user_id: {firstname, lastname, consult_cost, gender, bio, profile_pictures, hourly_consult_rate}}
    practitioner_details = {}
    for practitioner, consult_rate in practitioners:
        fd = FileDownload(practitioner.user_id)
        urls = {}
        for pic in practitioner.staff_profile.profile_pictures:
            if pic.original:
                continue
            urls[str(pic.width)] = fd.url(pic.image_path)

        # get presinged url to available practitioners' profile picture
        # it's done here so we only call S3 once per practitioner available
        practitioner_details[practitioner.user_id] = {
            'firstname': practitioner.firstname,
            'lastname': practitioner.lastname,
            'gender': 'm' if practitioner.biological_sex_male else 'f',
            'bio': practitioner.staff_profile.bio,
            'hourly_consult_rate': consult_rate,
            'consult_cost': calculate_consult_rate(consult_rate, duration),
            'profile_pictures': urls,
            'roles' : [role.role for role in practitioner.roles]}

    return practitioner_details

def verify_availability(
    client_user_id,
    staff_user_id,
    utc_start_idx,
    utc_end_idx,
    target_start_datetime_utc,
    target_end_datetime_utc,
    client_location_id):
    ###
    # Check to see the client and staff still have the requested time slot available
    # - current bookings
    # - staff availability
    #       - if staff from wheel, query wheel for availability
    #       - else, check the StaffAvailability table 
    ###
    
    # Bring up the current bookings for the staff and client
    # check to make sure there are no conflicts with the requested appointment time
    client_bookings = TelehealthBookings.query.filter(
            TelehealthBookings.client_user_id==client_user_id,
            TelehealthBookings.target_date_utc==target_start_datetime_utc.date(),
            TelehealthBookings.status!='Canceled').all()
    staff_bookings = TelehealthBookings.query.filter(
        TelehealthBookings.staff_user_id==staff_user_id,
        TelehealthBookings.target_date_utc==target_start_datetime_utc.date(),
        TelehealthBookings.status!='Canceled').all()

    # This checks if the input slots have already been taken.
    # using utc times to remain consistent 
    if client_bookings:
            for booking in client_bookings:
                if ((utc_start_idx >= booking.booking_window_id_start_time_utc and
                     utc_start_idx < booking.booking_window_id_end_time_utc) or
                    (utc_end_idx > booking.booking_window_id_start_time_utc and
                     utc_end_idx < booking.booking_window_id_end_time_utc)):
                    raise BadRequest('There already is a client appointment for this time.')

    if staff_bookings:
        for booking in staff_bookings:
            if ((utc_start_idx >= booking.booking_window_id_start_time_utc and
                    utc_start_idx < booking.booking_window_id_end_time_utc) or
                (utc_end_idx > booking.booking_window_id_start_time_utc and
                    utc_end_idx < booking.booking_window_id_end_time_utc)):
                raise BadRequest('There already is a practitioner appointment for this time.')

    ##
    # ensure staff still has the same availability
    # if staff is a wheel clinician, query wheel for their current availability
    ##
    ########### WHEEL #########
        # wheel = Wheel()
        # wheel_clinician_ids = wheel.clinician_ids(key='user_id')

    if False: #staff_user_id in wheel_clinician_ids:
        has_availability = wheel.openings(
            target_time_range = (target_start_datetime_utc-timedelta(minutes=5), target_end_datetime_utc+timedelta(minutes=5)), 
            location_id = client_location_id,
            clinician_id=wheel_clinician_ids[staff_user_id])[target_start_datetime_utc.date()].get(staff_user_id)
    else:
        # TODO consider day overlaps???
        staff_availability = db.session.execute(
            select(TelehealthStaffAvailability).
            filter(
                TelehealthStaffAvailability.booking_window_id.in_([idx for idx in range (utc_start_idx,utc_end_idx + 1)]),
                TelehealthStaffAvailability.day_of_week == DAY_OF_WEEK[target_start_datetime_utc.weekday()],
                TelehealthStaffAvailability.user_id == staff_user_id
                )
        ).scalars().all()
        # Make sure the full range of requested idices are found in staff_availability
        available_indices = {line.booking_window_id for line in staff_availability}
        requested_indices = {req_idx for req_idx in range(utc_start_idx, utc_end_idx + 1)}
        has_availability = requested_indices.issubset(available_indices)
    
    if not has_availability:
        raise BadRequest("Staff does not currently have this time available")

    return 

def update_booking_status_history(new_status: str, booking_id: int, reporter_id: int, reporter_role: str):
    # create TelehealthBookingStatus object
    status_history = TelehealthBookingStatus(
        booking_id = booking_id,
        reporter_id = reporter_id,
        reporter_role = reporter_role,
        status = new_status
    )
    # save TelehealthBookingStatus object connected to this booking.
    db.session.add(status_history)

def complete_booking(booking_id: int):
    """ Complete a booking.

    After booking gets started, make sure it gets completed

    1. Update booking status
    2. Send signal to twilio
    """
    # Query the booking in question & check status
    booking = TelehealthBookings.query.get(booking_id)
    if not booking:
        raise BadRequest('Meeting does not exist')
    
    if booking.status == 'Completed':
        return 'Booking Completed by Participants'
    
    elif booking.status != 'In Progress':
        raise BadRequest('Meeting has not started')

    # update status
    booking.status = 'Completed'

    # complete twilio room if making call over, catch error or raise if not expected error
    twilio = Twilio()
    twilio.complete_telehealth_video_room(booking_id)
    ##### WHEEL #####        
    # if booking.external_booking_id:
    #     wheel = Wheel()
    #     wheel.complete_consult(booking.external_booking_id)

    db.session.commit()
    return 'Booking Completed by System'

def add_booking_to_calendar(
    booking,
    booking_start_staff_localized,
    booking_end_staff_localized):
    add_to_calendar = StaffCalendarEvents(user_id=booking.staff_user_id,
                                        start_date=booking_start_staff_localized.date(),
                                        end_date=booking_end_staff_localized.date(),
                                        start_time=booking_start_staff_localized.strftime('%H:%M:%S'),
                                        end_time=booking_end_staff_localized.strftime('%H:%M:%S'),
                                        recurring=False,
                                        availability_status='Busy',
                                        location='Telehealth_'+str(booking.idx),
                                        description='',
                                        all_day=False,
                                        timezone = booking_start_staff_localized.astimezone().tzname()
                                        )
    db.session.add(add_to_calendar)

def get_booking_increment_data():
    global booking_time_increment_length
    global booking_max_increment_idx

    if booking_time_increment_length == 0 or booking_max_increment_idx == 0:
        #values have not been calculated yet


        last_increment = LookupBookingTimeIncrements.query.all()[-1]
        increment_length = (datetime.combine(date.min, last_increment.end_time) -  \
            datetime.combine(date.min, last_increment.start_time))
        #convert time delta to minutes
        booking_time_increment_length = (increment_length.seconds % 3600) // 60
        booking_max_increment_idx = last_increment.idx

    return({'length': booking_time_increment_length,
            'max_idx': booking_max_increment_idx})
