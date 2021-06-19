from base64 import b64encode
from datetime import datetime, timedelta

from flask.json import dumps
from sqlalchemy import and_, or_, select
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.notifications.models import Notifications
from odyssey.api.telehealth.models import TelehealthBookings

from odyssey.api.user.models import User
from tests.functional.telehealth.client_select_data import telehealth_staff_full_avilability, telehealth_bookings_data_full_day

from odyssey.tasks.periodic import deploy_upcoming_appointment_notifications
from odyssey.tasks.tasks import upcoming_appointment_notification_2hr



def test_upcoming_bookings_scan(test_client, init_database, staff_auth_header):
    """
    Add availability for a staff member for two consecutive days
    Book clients to the staff member accross windows
    """
    ##
    # Submit availability for staff memeber
    ##

    # log in staff member, submit availability
    staff_member = init_database.session.execute(
        select(User).
        where(User.is_staff == True).
        order_by(User.user_id)
    ).scalars().all()[-1]
    valid_credentials = b64encode(
            f"{staff_member.email}:{'password'}".encode(
                "utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')
    auth_header = {'Authorization': f'Bearer {token}'}

    # generate availability
    response = test_client.post(f'/telehealth/settings/staff/availability/{staff_member.user_id}/',
                                headers=auth_header, 
                                data=dumps(telehealth_staff_full_avilability), 
                                content_type='application/json')

    ##
    # Sign in as a client, book appointments with the staff member above
    ##

    # log in as a user, make bookings
    client = init_database.session.execute(
        select(User).
        where(User.is_client == True).
        order_by(User.user_id)
    ).scalars().all()[-1]
    valid_credentials = b64encode(
            f"{client.email}:{'password'}".encode(
                "utf-8")).decode("utf-8")
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')
    auth_header = {'Authorization': f'Bearer {token}'}

    # loop through all bookings in test data 
    for booking in telehealth_bookings_data_full_day:
        #add to queue
        queue_data = {
                'profession_type': 'Medical Doctor',
                'target_date': datetime.strptime(
                    booking.get('target_date'), '%Y-%m-%d').isoformat(),
                'priority': False,
                'medical_gender': 'np'
            }
        response = test_client.post(f'/telehealth/queue/client-pool/{client.user_id}/',
                                headers=auth_header, 
                                data=dumps(queue_data), 
                                content_type='application/json')

        response = test_client.post('/telehealth/bookings/?client_user_id={}&staff_user_id={}'.format(client.user_id,staff_member.user_id),
                                headers=auth_header, 
                                data=dumps(booking), 
                                content_type='application/json')

        assert response.status_code == 201

    ###
    # Test tasks.periodic.deploy_upcoming_appointment_notifications
    # - scanning windows for upcoming bookings:
    #   (booking_window_id_start - booking_window_id_end, actual times)
    #   1 - 96    (00:00 - 08:00)
    #   73 - 168  (06:00 - 14:00)
    #   145 - 240 (12:00 - 20:00)
    #   217 - 24  (18:00 - 02:00)
    #   1 - 96    (00:00 - 08:00) <-next day
    ###

    target_date = datetime.strptime('2022-04-04', '%Y-%m-%d')
    
    upcoming_bookings_1 = deploy_upcoming_appointment_notifications(
        target_date=target_date,
        booking_window_id_start=1,
        booking_window_id_end=96)
    
    upcoming_bookings_2 = deploy_upcoming_appointment_notifications(
        target_date=target_date,
        booking_window_id_start=73,
        booking_window_id_end=168)
    
    upcoming_bookings_3 = deploy_upcoming_appointment_notifications(
        target_date=target_date,
        booking_window_id_start=145,
        booking_window_id_end=240)

    upcoming_bookings_4 = deploy_upcoming_appointment_notifications(
        target_date=target_date,
        booking_window_id_start=217,
        booking_window_id_end=24)

    upcoming_bookings_5 = deploy_upcoming_appointment_notifications(
        booking_window_id_start=1,
        booking_window_id_end=96,
        target_date=target_date+timedelta(days=1))

    # no target_date set
    upcoming_bookings_today = deploy_upcoming_appointment_notifications(
        booking_window_id_start=1,
        booking_window_id_end=96)

    all_bookings_day_1 = init_database.session.execute(
        select(TelehealthBookings).
        where(TelehealthBookings.target_date == target_date)
    ).scalars().all()
    
    all_bookings_day_2 = init_database.session.execute(
        select(TelehealthBookings).
        where(TelehealthBookings.target_date == target_date+timedelta(days=1), TelehealthBookings.booking_window_id_end_time<=96)
    ).scalars().all()

    # Check to make sure all bookings were picked up
    upcoming_all = list(set(upcoming_bookings_1+upcoming_bookings_2+upcoming_bookings_3+upcoming_bookings_4+upcoming_bookings_5))

    assert len(upcoming_all) == len(all_bookings_day_1+all_bookings_day_2)
    assert upcoming_bookings_today == []
    ##
    # Test upcoming appointment notification task
    #
    ##
    test_booking = upcoming_bookings_4[0]
    
    test_booking_start_time = init_database.session.execute(
        select(LookupBookingTimeIncrements).
        where(LookupBookingTimeIncrements.idx == test_booking.booking_window_id_start_time)
        ).scalars().one_or_none()

    # call celery task: odyssey.tasks.tasks.upcoming_appointment_notification_2hr
    upcoming_appointment_notification_2hr(test_booking.idx)

    notifications = init_database.session.execute(
        select(Notifications).
        where(Notifications.notification_type_id == 2,
            or_(Notifications.user_id == test_booking.client_user_id, 
            Notifications.user_id == test_booking.staff_user_id))).scalars().all()
    
    assert notifications[0].expires == datetime.combine(test_booking.target_date, test_booking_start_time.start_time) + timedelta(hours=2)

 
