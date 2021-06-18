from datetime import datetime, timedelta

from sqlalchemy import or_, select

from odyssey import celery, db
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.notifications.models import Notifications
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.user.models import User

@celery.task()
def upcoming_appointment_notification_2hr(booking_id):
    """
    Store notification of upcoming appointment in the Notifications table
    One for each user
    """

    # bring up the booking and the user objects for the booking attendees
    booking = db.session.execute(
        select(TelehealthBookings).
        where(TelehealthBookings.idx == booking_id, TelehealthBookings.status == 'Accepted')
    ).scalars().one_or_none()

    if not booking:
        return

    staff_user = db.session.execute(
        select(User).
        where(User.user_id == booking.staff_user_id)
    ).scalars().one_or_none()

    client_user = db.session.execute(
        select(User).
        where(User.user_id == booking.client_user_id)
    ).scalars().one_or_none()

    # look up the start time and create dt object for the notification expire time (2 hours after the appointment begins)
    start_time = db.session.execute(
        select(LookupBookingTimeIncrements.start_time).
        where(LookupBookingTimeIncrements.idx == booking.booking_window_id_start_time_utc)
    ).scalars().one_or_none()
    
    start_dt = datetime.combine(booking.target_date, start_time)
    expires_at = start_dt+timedelta(hours=2)
    
    # check if either notification exists before adding to database
    # this is meant to prevent duplicate inputs.
    existing_staff_notification = db.session.execute(
        select(Notifications).
        where(Notifications.user_id == staff_user.user_id, 
              Notifications.expires == expires_at, 
              Notifications.notification_type_id == 2)
        ).scalars().one_or_none()
    
    existing_client_notification = db.session.execute(
        select(Notifications).
        where(Notifications.user_id == client_user.user_id, 
              Notifications.expires == expires_at, 
              Notifications.notification_type_id == 2)
        ).scalars().one_or_none()
    
    # create the staff and client notification entries
    if not existing_staff_notification:
        staff_notification = Notifications(
            user_id=booking.staff_user_id,
            title="You have a telehealth appointment in 2 hours",
            content=f"Your telehealth appointment with {client_user.firstname+' '+client_user.lastname} is in 2 hours. Please review your client's medical information before taking the call.",
            expires = expires_at,
            notification_type_id = 2 #Scheduling
        )
        db.session.add(staff_notification)
    
    if not existing_client_notification:
        client_notification = Notifications(
            user_id=booking.client_user_id,
            title="You have a telehealth appointment in 2 hours",
            content=f"Your telehealth appointment with {staff_user.firstname+' '+staff_user.lastname} is in 2 hours. Please ensure your medical information is up to date before taking the call.",
            expires = expires_at,
            notification_type_id = 2 #Scheduling
        )
        db.session.add(client_notification)

    db.session.commit()

    return
