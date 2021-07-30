from base64 import b64encode
from datetime import datetime, timedelta
from random import choice

from flask.json import dumps
from sqlalchemy import and_, or_, select
from odyssey.api.client.models import ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupBookingTimeIncrements, LookupClinicalCareTeamResources, LookupEHRPages
from odyssey.api.notifications.models import Notifications
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.payment.models import PaymentMethods

from odyssey.api.user.models import User
from tests.functional.telehealth.client_select_data import(
    telehealth_staff_full_availability,
    telehealth_bookings_data_full_day,
    payment_method_data)

from odyssey.tasks.periodic import deploy_upcoming_appointment_tasks
from odyssey.tasks.tasks import upcoming_appointment_notification_2hr, upcoming_appointment_care_team_permissions

# from odyssey.tests.utils import login

def test_upcoming_bookings_scan(test_client):
    global upcoming_bookings_all
    ##
    # Submit availability for staff memeber
    ##

    # generate availability
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_full_availability),
        content_type='application/json')

    ##
    # Sign in as a client, book appointments with the staff member above
    ##

    # add payment method to db
    # test_client.post(
    #     f'/payment/methods/{client.user_id}/',
    #     headers=auth_header,
    #     data=dumps(payment_method_data['normal_data']),
    #     content_type='application/json')
    payment_method = PaymentMethods.query.filter_by(user_id=test_client.client_id).first()

    # loop through all bookings in test data
    for booking in telehealth_bookings_data_full_day:
        #add to queue
        queue_data = {
            'profession_type': 'medical_doctor',
            'target_date': datetime.strptime(
                booking.get('target_date'), '%Y-%m-%d').isoformat(),
            'priority': False,
            'medical_gender': 'np',
            'location_id': 1,
            'payment_method_id': payment_method.idx}

        response = test_client.post(
            f'/telehealth/queue/client-pool/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            data=dumps(queue_data),
            content_type='application/json')

        response = test_client.post(
            f'/telehealth/bookings/?client_user_id={test_client.client_id}&staff_user_id={test_client.staff_id}',
            headers=test_client.client_auth_header,
            data=dumps(booking),
            content_type='application/json')

        assert response.status_code == 201

    ###
    # Test tasks.periodic.deploy_upcoming_appointment_tasks
    # - scanning windows for upcoming bookings:
    #   (booking_window_id_start - booking_window_id_end, actual times)
    #   1 - 96    (00:00 - 08:00)
    #   73 - 168  (06:00 - 14:00)
    #   145 - 240 (12:00 - 20:00)
    #   217 - 24  (18:00 - 02:00)
    #   1 - 96    (00:00 - 08:00) <-next day
    ###

    target_date = datetime(2022, 4, 4)

    upcoming_bookings_1 = deploy_upcoming_appointment_tasks(
        target_date=target_date,
        booking_window_id_start=1,
        booking_window_id_end=96)

    upcoming_bookings_2 = deploy_upcoming_appointment_tasks(
        target_date=target_date,
        booking_window_id_start=73,
        booking_window_id_end=168)

    upcoming_bookings_3 = deploy_upcoming_appointment_tasks(
        target_date=target_date,
        booking_window_id_start=145,
        booking_window_id_end=240)

    upcoming_bookings_4 = deploy_upcoming_appointment_tasks(
        target_date=target_date,
        booking_window_id_start=217,
        booking_window_id_end=24)

    upcoming_bookings_5 = deploy_upcoming_appointment_tasks(
        booking_window_id_start=1,
        booking_window_id_end=96,
        target_date=target_date+timedelta(days=1))

    # no target_date set
    upcoming_bookings_today = deploy_upcoming_appointment_tasks(
        booking_window_id_start=1,
        booking_window_id_end=96)

    all_bookings_day_1 = test_client.db.session.execute(
        select(TelehealthBookings)
        .where(TelehealthBookings.target_date == target_date)
    ).scalars().all()

    all_bookings_day_2 = test_client.db.session.execute(
        select(TelehealthBookings)
        .where(
            TelehealthBookings.target_date == target_date + timedelta(days=1),
            TelehealthBookings.booking_window_id_end_time <= 96)
    ).scalars().all()

    # Check to make sure all bookings were picked up
    upcoming_bookings_all = list(set(
        upcoming_bookings_1 
        + upcoming_bookings_2
        + upcoming_bookings_3
        + upcoming_bookings_4
        + upcoming_bookings_5))

    assert len(upcoming_bookings_all) == len(all_bookings_day_1 + all_bookings_day_2)
    assert upcoming_bookings_today == []

def test_upcoming_bookings_notification(test_client):
    ##
    # Test upcoming appointment notification task
    #
    ##

    test_booking = choice(upcoming_bookings_all)

    test_booking_start_time = test_client.db.session.execute(
        select(LookupBookingTimeIncrements)
        .where(
            LookupBookingTimeIncrements.idx == test_booking.booking_window_id_start_time)
        ).scalars().one_or_none()

    # call celery task: odyssey.tasks.tasks.upcoming_appointment_notification_2hr
    upcoming_appointment_notification_2hr(test_booking.idx)

    notifications = test_client.db.session.execute(
        select(Notifications).
        where(
            Notifications.notification_type_id == 2,
            or_(
                Notifications.user_id == test_booking.client_user_id,
                Notifications.user_id == test_booking.staff_user_id))
        ).scalars().all()

    assert notifications[0].expires == (
        datetime.combine(
            test_booking.target_date,
            test_booking_start_time.start_time)
        + timedelta(hours=2))

def test_upcoming_bookings_notification(test_client):
    ##
    # Test upcoming appointment ehr permissions task
    #
    ##
    test_booking = choice(upcoming_bookings_all)
    upcoming_appointment_care_team_permissions(test_booking.idx)

    care_team_permissions = (test_client.db.session.execute(
        select(ClientClinicalCareTeamAuthorizations)
        .where(
            ClientClinicalCareTeamAuthorizations.user_id == test_booking.client_user_id,
            ClientClinicalCareTeamAuthorizations.team_member_user_id == test_booking.staff_user_id))
        .scalars()
        .all())

    resource_ids_needed = (test_client.db.session.execute(
        select(
            LookupClinicalCareTeamResources.resource_id,
            LookupEHRPages.resource_group_id)
        .join(
            LookupEHRPages,
            LookupEHRPages.resource_group_id == LookupClinicalCareTeamResources.resource_group_id)
        .where(
            LookupEHRPages.access_group.in_(['general', 'medical_doctor'])))
        .scalars()
        .all())

    assert len(care_team_permissions) == len(resource_ids_needed)
