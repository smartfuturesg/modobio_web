from datetime import datetime, date, timedelta

from celery.schedules import crontab
from flask import current_app
from sqlalchemy import delete, text
from sqlalchemy import and_, or_, select

from odyssey import celery, db
from odyssey.tasks.tasks import upcoming_appointment_notification_2hr
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.client.models import ClientDataStorage
from odyssey.api.lookup.models import LookupBookingTimeIncrements

@celery.task()
def refresh_client_data_storage():
    """
    Use data_per_client view to update ClientDataStorage table
    """
    dat = db.session.execute(
        text("SELECT * FROM public.data_per_client")
    ).all()
    db.session.execute(delete(ClientDataStorage))
    db.session.flush()

    for row in dat:
        db.session.add(ClientDataStorage(user_id=row[0], total_bytes=row[1], storage_tier=row[2]))
    db.session.commit()

    return

@celery.task()
def deploy_upcoming_appointment_notifications(booking_window_id_start, booking_window_id_end, target_date=None):
    """
    Scan bookings for upcoming appointments. Deploy scheduled tasks which add an upcoming appointment
    notification to the UserNotification table within 2 hours of the booking. 

    00:00 - 08:00
    06:00 - 14:00
    12:00 - 20:00
    18:00 - 02:00
    00:00 - 08:00 

    Parameters
    ----------
    target_date : to be used if testing. Otherwise date is set using system time (UTC)
    booking_window_id_start: start of booking window provided in UTC
    booking_window_id_end: end of booking window provided in UTC
    """
    # grab the current date for the queries below
    if not target_date:
        target_date = date.today()
    
    # compensate for scanning window inbetween days
    if booking_window_id_start > booking_window_id_end:
        # bookings beginning on current day
        bookings_1 = db.session.execute(
            select(TelehealthBookings). 
                where(and_(
                TelehealthBookings.target_date_utc==target_date, 
                TelehealthBookings.booking_window_id_start_time_utc >= booking_window_id_start , #18:00
                or_( # meeting ends between 18:00 and 02:00
                    TelehealthBookings.booking_window_id_end_time_utc <= booking_window_id_end, #02:00
                    TelehealthBookings.booking_window_id_end_time_utc > booking_window_id_start),
                )) 
            ).scalars().all()

        # bookings begining on following day of scanning window
        bookings_2 = db.session.execute(
            select(TelehealthBookings). 
            where(and_(
                TelehealthBookings.target_date_utc==target_date+timedelta(days=1), 
                TelehealthBookings.booking_window_id_start_time_utc >= 0 , #00:00
                TelehealthBookings.booking_window_id_end_time_utc <= booking_window_id_end, #02:00
                )) 
            ).scalars().all()
        upcoming_bookings = bookings_1 + bookings_2
    else:
        upcoming_bookings = db.session.execute(
            select(TelehealthBookings). 
            where(and_(
                TelehealthBookings.target_date_utc==target_date, 
                TelehealthBookings.booking_window_id_start_time_utc >= booking_window_id_start , 
                TelehealthBookings.booking_window_id_end_time_utc <= booking_window_id_end, 
                )) 
            ).scalars().all()

    # do not deploy appointment notifications in testing
    if current_app.config['TESTING']:
        return upcoming_bookings
    
    #schedule appointment notification tasks for 2 hrs before appointment
    for booking in upcoming_bookings:
        # create datetime object for scheduling tasks
        booking_start_time = db.session.execute(
                select(LookupBookingTimeIncrements.start_time).
                where(LookupBookingTimeIncrements.idx == booking.booking_window_id_start_time_utc)
            ).scalars().one_or_none()
        notification_eta = datetime.combine(booking.target_date_utc, booking_start_time) - timedelta(hours = 2)

        # Deploy scheduled task to update notifications table with upcoming booking notification
        upcoming_appointment_notification_2hr.apply_async((booking.idx,),eta=notification_eta)

    return 



celery.conf.beat_schedule = {
    # refresh the client data storage table every day at midnight
    'add-update-client-data-storage-table': {
        'task': 'odyssey.tasks.periodic.refresh_client_data_storage',
        'schedule': crontab(hour=0, minute=0)
    },
    # look for upcoming apppointment within moving windows:
    # (00:00 - 08:00)
    'check-for-upcoming-bookings-00-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_notifications',
         'args': (1, 96),
        'schedule': crontab(hour=0, minute=0)
    },
    # (06:00 - 14:00)
    'check-for-upcoming-bookings-06-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_notifications',
         'args': (73, 168),
        'schedule': crontab(hour=6, minute=0)
    },
    # (12:00 - 20:00)
    'check-for-upcoming-bookings-12-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_notifications',
         'args': (145, 240),
        'schedule': crontab(hour=12, minute=0)
    },
    # (18:00 - 02:00, Next day)
    'check-for-upcoming-bookings-18-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_notifications',
         'args': (217, 24),
        'schedule': crontab(hour=18, minute=0)
    },
}
