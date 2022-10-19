import logging
from flask import current_app
import boto3
from boto3.dynamodb.conditions import Attr
from odyssey.api.dosespot.models import DoseSpotPractitionerID
from odyssey.integrations.dosespot import DoseSpot

from datetime import datetime, time, timedelta, timezone
from celery.schedules import crontab
from celery.signals import worker_process_init, worker_ready   
from celery.utils.log import get_task_logger
from sqlalchemy import delete, text
from sqlalchemy import and_, or_, select
from odyssey import celery, db, mongo
from odyssey.tasks.base import BaseTaskWithRetry
from odyssey.tasks.tasks import (
    upcoming_appointment_care_team_permissions,
    upcoming_appointment_notification_2hr,
    charge_telehealth_appointment,
    store_telehealth_transcript,
    cancel_noshow_appointment,
    update_client_subscription_task,
    notify_client_of_imminent_scheduled_maintenance,
    notify_staff_of_imminent_scheduled_maintenance,
    upcoming_booking_payment_notification,
)
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthStaffAvailabilityExceptions, TelehealthChatRooms
from odyssey.api.client.models import ClientClinicalCareTeamAuthorizations, ClientDataStorage, ClientClinicalCareTeam
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.notifications.schemas import NotificationSchema
from odyssey.api.user.models import User, UserSubscriptions
from odyssey.utils.constants import TELEHEALTH_BOOKING_TRANSCRIPT_EXPIRATION_HRS, NOTIFICATION_SEVERITY_TO_ID, NOTIFICATION_TYPE_TO_ID
from odyssey.utils.misc import get_time_index, create_notification, cancel_telehealth_appointment

logger = get_task_logger(__name__)


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
def deploy_upcoming_appointment_tasks():
    """
    This task will scan the TelehealthBookings table for appointments that are not yet notified and
    are less than 2 hours away. It will then create a notification for the client and practitioner 
    involved with the booking and deploy the needed ehr permissions to the practitioner.
    """
    #get all bookings that are sheduled <2 hours away and have not been notified yet
    logger.info('deploying upcoming appointments task')
    current_time = datetime.now(timezone.utc) 
    target_time = current_time + timedelta(hours=2)
    target_time_window_start = get_time_index(datetime.now(timezone.utc))
    target_time_window_end = get_time_index(target_time)
    logger.info(f'upcoming bookings task time window: {target_time_window_start} - {target_time_window_end}')
    
    #find all accepted bookings who have not been notified yet
    bookings = TelehealthBookings.query.filter(TelehealthBookings.status == 'Accepted', TelehealthBookings.notified == False)
    if target_time_window_start > target_time_window_end:
        #this will happen from 22:00 to 23:55
        #in this case, we have to query across two dates
        bookings = \
            bookings.filter(
            or_(
                and_(
                    TelehealthBookings.booking_window_id_start_time_utc >= target_time_window_start,
                    TelehealthBookings.target_date_utc == current_time.date()
                ),
                and_(
                    TelehealthBookings.booking_window_id_start_time_utc <= target_time_window_end,
                    TelehealthBookings.target_date_utc == target_time.date()
                )
            )
            ).all()
    else:
        #otherwise just query for bookings whose start id falls between the target times on for today
        bookings =  \
            bookings.filter(
            and_(
                    TelehealthBookings.booking_window_id_start_time_utc >= target_time_window_start,
                    TelehealthBookings.booking_window_id_start_time_utc <= target_time_window_end,
                    TelehealthBookings.target_date_utc == target_time.date()
                    )
            ).all()

    # do not deploy appointment notifications in testing
    if current_app.config['TESTING']:
        for booking in bookings:
            booking.notified = True
        db.session.commit()
        return bookings
    
    #schedule pre-appointment tasks
    for booking in bookings:
        logger.info(f'deploying notifcation and care team tasks for booking with id {booking.idx}')
        booking.notified = True
        # create datetime object for scheduling tasks
        booking_start_time = db.session.execute(
                select(LookupBookingTimeIncrements.start_time).
                where(LookupBookingTimeIncrements.idx == booking.booking_window_id_start_time_utc)
            ).scalars().one_or_none()
        notification_eta = datetime.combine(booking.target_date_utc, booking_start_time) - timedelta(hours = 2)
        ehr_permissions_eta = datetime.combine(booking.target_date_utc, booking_start_time) - timedelta(minutes = 30)

        # Deploy scheduled task to update notifications table with upcoming booking notification
        upcoming_appointment_notification_2hr.apply_async((booking.idx,),eta=notification_eta)
        upcoming_appointment_care_team_permissions.apply_async((booking.idx,),eta=ehr_permissions_eta)
    db.session.commit()
    logger.info('upcoming bookings task completed')


@celery.task()
def deploy_appointment_transcript_store_tasks(target_date=None):
    """
    Following the completion of a telehealth appointment, the practitioner and client have a window of opportunity to add messages
    to the booking transcript. After this window, we will lock the conversation on twilio and store the transcript on the modobio end. 

    Parameters
    ----------
    target_date : date of chat room write access timeout
 
    """
    # target date argument is meant for testing only
    if not target_date:
        target_datetime_window = datetime.utcnow() + timedelta(hours=24)
    else:
        target_datetime_window = target_date + timedelta(hours=24)

    # search for chatroom write_access_timeouts that occur before this time and have not yet been stored on the modobio end
    chatrooms = db.session.execute(
        select(TelehealthChatRooms).
        where(
            TelehealthChatRooms.write_access_timeout <= target_datetime_window,
            TelehealthChatRooms.transcript_object_id == None)
    ).scalars().all()

    # do not deploy task in testing
    if current_app.config['TESTING']:
        return chatrooms

    for chat in chatrooms:
        # Deploy scheduled task 
        store_telehealth_transcript.apply_async((chat.booking_id,),eta=chat.write_access_timeout)

    return 


@celery.task()
def cleanup_temporary_care_team():
    """
    This method accomplishes 2 tasks regarding temporary care team members:

    -Temporary members that have less than 24 hours (>= 156 hours since being granted access)
    remaining will trigger a notification for the user whose team they are on.
    -Temporary members who have had access for >= 180 hours will be removed.
    """
    notification_time = datetime.utcnow()-timedelta(hours=156)
    expire_time = datetime.utcnow()-timedelta(hours=180)

    #find temporary members who are within 24 hours of expiration
    notifications = db.session.execute(
        select(ClientClinicalCareTeam). 
                where(and_(
                ClientClinicalCareTeam.created_at <= notification_time, 
                ClientClinicalCareTeam.created_at > expire_time,
                ClientClinicalCareTeam.is_temporary == True)
            )).scalars().all()

    for notification in notifications:
        #create notification that care team member temporary access is expiring
        member = User.query.filter_by(user_id=notification.team_member_user_id).one_or_none()
        
        create_notification(
            notification.team_member_user_id,
            NOTIFICATION_SEVERITY_TO_ID.get('High'),
            NOTIFICATION_TYPE_TO_ID.get('Team'),
            f'{member.firstname} {member.lastname}\'s Data Access Is About To Expire',
            f'Would you like to add {member.firstname} {member.lastname} to your team?' \
            'Swipe right on their entry in your team list to make them a permanent member of your team!',
            'Provider'
        )

    #find all temporary members that are older than the 180 hour limit
    expired = db.session.execute(
        select(ClientClinicalCareTeam).
            where(and_(
                ClientClinicalCareTeam.created_at <= expire_time,
                ClientClinicalCareTeam.is_temporary == True
            ))
        ).scalars().all()

    for item in expired:
        # lookup granted permissions, delete those too
        permissions = db.session.execute(select(ClientClinicalCareTeamAuthorizations
        ).where(
            and_(ClientClinicalCareTeamAuthorizations.team_member_user_id == item.team_member_user_id,
            ClientClinicalCareTeamAuthorizations.user_id == item.user_id
        ))).scalars().all()

        for permission in permissions:
            db.session.delete(permission)

        db.session.delete(item)
    
    db.session.commit()


@celery.task(base=BaseTaskWithRetry)
def deploy_webhook_tasks(**kwargs):
    """
    **Deprecated 5.13.22** Leaving this here because it is a pattern we will want to use for future webhook integrations

    This is a persistent background task intended to listen for new entries into the webhook database.
    Each entry represents a webhook request from a third party service. When inserts are detected, this task will 
    deploy a separate task to handle the webhook request accordingly. 

    The following steps are taken to ensure each request is handled:
    1. Scan monogoDB webhooks database for any unprocessed webhooks. These will be entries which are not labeled as acknowledged
        or processed. 
    2. Fire off the tasks accordingly, including the full webhook payload. 
    3. Open a change stream in order to listen to changes in the webhook database. The listener is set to only react to
        inserts. All other operations are ignored. 
    4. Send the full payloads to the appropriate task handler.

    As this task is intended to be running constantly in the background, it is called right when the celery workers are 
    done initializing by the `tasks.periodic.startup_tasks` function.

    TODO: details on maintaining persistence in case of failures like temporary outage of mongodb. 
    """
    # create a change stream object on it filtering by only insert operations
    # This step must be done first so that no entries are lost between now and the following step
    stream = mongo.db.watch([{'$match': {'operationType': {'$in': ['insert'] }}}])

    # search for currently unprocessed webhook tasks, handle them accordingly
    # NOTE: each integration is given a colelction in the webhook database. MongoDB allows searching only one collection 
    # at a time. So this step must be done for each integration
    # unprocessed_wheel_wh = mongo.db.wheel.find({ "$or" : [{"modobio_meta.processed":False} , {"modobio_meta.acknowleged" : False}]})

    # # send wheel payloads for processing
    # for wh_payload in unprocessed_wheel_wh:
    #     wh_payload['_id'] = str(wh_payload['_id'])
    #     logger.info("deploying task originating from wheel webhook")
    #     process_wheel_webhooks.delay(wh_payload)

    # # open while loop waits for new inserts to the database from any collection
    # while True:
    #     wh_payload = stream.try_next()
    #     if wh_payload:
    #         wh_payload['fullDocument']['_id'] = str(wh_payload['fullDocument']['_id'])
    #         logger.info(f"deploying task originating from {wh_payload['ns']['coll']} webhook")
    #         # shoot off background task for each integration accordingly 
    #         if wh_payload['ns']['coll'] == 'wheel':
    #             process_wheel_webhooks.delay(wh_payload['fullDocument'])

    pass


# @worker_ready.connect()
def startup_tasks(**kwargs):
    """ **Deprecated 5.13.22** leave here for future webhook tasks"""
    deploy_webhook_tasks.delay()


@celery.task()
def find_chargable_bookings():
    """
    This task will scan the TelehealthBookings table for appointments that are not yet paid and
    are less than 24 hours away. It will then charge the user for the appointment using the 
    payment method saved to the booking.
    """
    #get all bookings that are scheduled <24 hours away and have not been charged yet
    logger.info('deploying charge booking task')
    target_time = datetime.now(timezone.utc) + timedelta(hours=24)
    target_time_window = get_time_index(target_time)
    logger.info(f'charge bookings task time window: {target_time_window}')
    
    bookings = TelehealthBookings.query.filter(TelehealthBookings.charged == False, TelehealthBookings.status == 'Accepted') \
        .filter(or_(
            and_(TelehealthBookings.booking_window_id_start_time_utc >= target_time_window, TelehealthBookings.target_date_utc == datetime.now(timezone.utc).date()),
            and_(TelehealthBookings.booking_window_id_start_time_utc <= target_time_window, TelehealthBookings.target_date_utc == target_time.date())
        )).all()
    
    # do not deploy charge task in testing
    if current_app.config['TESTING']:
        return bookings

    for booking in bookings:
        logger.info(f'chargable booking detected with id {booking.idx}')
        booking.charged = True
        db.session.commit()
        charge_telehealth_appointment.apply_async((booking.idx,), eta=datetime.now())
    logger.info('charge booking task completed')


@celery.task()
def detect_practitioner_no_show():
    """
    This task will scan the TelehealthBookings table for bookings where the practitioner does not
    join the call on time. If a practitioner does not start a telehealth call within 10 minutes of
    the scheduled time, the client will be refunded for the booking.
    """
    logger.info("deploying practitioner no show task")
    target_time = datetime.now(timezone.utc)
    target_time_window = get_time_index(target_time)
    if target_time_window <= 2:
        #if it is 12:00 or 12:05, we have to adjust to target the previous date at 11:50 and 11:55 respectively
        target_time = target_time - timedelta(hours=24)
        target_time_window = 288 + target_time_window
    logger.info(f'no show task time window: {target_time_window}')

    bookings = TelehealthBookings.query.filter(TelehealthBookings.status == 'Accepted', 
                                               #TelehealthBookings.charged == True,
                                               TelehealthBookings.target_date_utc == target_time.date(),
                                               TelehealthBookings.booking_window_id_start_time_utc <= target_time_window - 2).all()
    for booking in bookings:
        logger.info(f'no show detected for the booking with id {booking.idx}')
        #change booking status to canceled and refund client
        if current_app.config['TESTING']:
            #cancel_noshow_appointment(booking.idx)
            cancel_telehealth_appointment(booking, reason='Practitioner No Show')
        else:
            cancel_noshow_appointment.apply_async((booking.idx,), eta=datetime.now())
    logger.info('no show task completed')


@celery.task()
def get_dosespot_notifications():
    """
    Populate dosespot notifications for all practitioners registered on the DS platform
    """
    # bring up all ds practitioners

    ds_practitioners = DoseSpotPractitionerID.query.all()
    
    for practitioner in ds_practitioners:
        ds = DoseSpot()
        ds.practitioner_ds_id = practitioner.ds_user_id
        ds.notifications(practitioner.user_id) 


@celery.task()
def deploy_subscription_update_tasks(interval:int):
    """
    Checks for subscriptions that are near expiration and then shoots off tasks to 
    check if those subscriptions have been renewed. 
    
    Parameters
    ----------
    interval: int
        Sets time window where upcoming subscription expirations will be checked for updates. Corresponds
        to the frequency of this periodic task. 
 
    """
    # check for subscriptions expiring in the near future
    expired_by = datetime.utcnow() + timedelta(minutes = interval)

    subscriptions = db.session.execute(
        select(UserSubscriptions). 
        where(UserSubscriptions.expire_date < expired_by, UserSubscriptions.subscription_status == 'subscribed'
            )).scalars().all()
    
    for subscription in subscriptions:
        logger.info(f"Deploying task to update subscription for user_id: {subscription.user_id}")
        # buffer task eta to ensure subscription has been updated on apple's end by the time this task runs
        task_eta = subscription.expire_date 
        if task_eta < datetime.utcnow():
            update_client_subscription_task.delay(subscription.user_id)
        else:
            update_client_subscription_task.apply_async((subscription.user_id,),eta=task_eta)
    
    return 


@celery.task()
def remove_expired_availability_exceptions():
    """
    Checks for availability exceptions whose exception_date is in the past and removes them.
    """
    
    current_date = datetime.now(timezone.utc).date()
    logger.info('Deploying remove expired exceptions test')
    exceptions = TelehealthStaffAvailabilityExceptions.query.filter(
        TelehealthStaffAvailabilityExceptions.exception_date < current_date
    ).all()
    
    for exception in exceptions:
        db.session.delete(exception)
    db.session.commit()
    logger.info('Completed remove expired exceptions task')


@worker_process_init.connect
def close_previous_db_connection(**kwargs):
    if db.session:
        db.session.close()
        db.engine.dispose()


@celery.task()
def create_subtasks_to_notify_clients_and_staff_of_imminent_scheduled_maintenance():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(current_app.config['MAINTENANCE_DYNAMO_TABLE'])

    now_string = (datetime.utcnow() - timedelta(seconds=10)).strftime("%Y-%m-%dT%H:%M:%S.000000+00:00")
    one_hour_15min_out_string = (datetime.utcnow() + timedelta(hours=1, minutes=15, seconds=10)).strftime("%Y-%m-%dT%H:%M:%S.000000+00:00")

    response = table.scan(  # look for imminent scheduled maintenances
        FilterExpression=Attr('deleted').eq('False') &
        Attr('start_time').between(now_string, one_hour_15min_out_string) &
        Attr('notified').eq('False')
    )  # runs every 15 minutes, so reach out an extra 14 minutes
    # better that notifications are generated a bit early rather than late
    data = response['Items']
    # if data is empty, this for loop will not run
    for datum in data:  # should only ever be one, but just in case
        # create tasks to alert client users of the imminent maintenance
        for client in User.query.filter_by(is_client=True, deleted=False).all():
            notify_client_of_imminent_scheduled_maintenance.delay(client.user_id, datum)
        # create tasks to alert staff users of the imminent maintenance
        for staff in User.query.filter_by(is_staff=True, deleted=False).all():
            notify_staff_of_imminent_scheduled_maintenance.delay(staff.user_id, datum)
        # must now set notified attr of scheduled maintenance(s) to be True, was set to False on posting
        table.update_item(
            Key={'block_id': datum['block_id']},
            UpdateExpression="set #notified = :notified",
            ExpressionAttributeNames={'#notified': 'notified'},
            ExpressionAttributeValues={':notified': "True"},
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f'Maintenance with block_id:{datum["block_id"]} had notifications for it sent to client and staff.')


@celery.task()
def check_for_upcoming_booking_charges():
    """
    This  will scan the TelehealthBookings table for appointments that are at most 48 hours away
    and that have payment_notified: False.
    Bookings are charged 24 hours in advance, so these will be charged in just under 24 hours. Runs every 6 minutes
    Subtasks for each booking will have a notification generated alerting clients they will be charged in 24 hours.
    """
    # get all bookings that are scheduled up to 48 hours away and have payment_notified: False
    logger.info('deploying check_for_upcoming_booking_charges task')
    time_now = datetime.utcnow()
    middle_dt = time_now + timedelta(days=1)
    target_time = time_now + timedelta(days=2)
    target_time_window = get_time_index(target_time)
    logger.info(f'Upcoming bookings charges task checking time window: {time_now} to {target_time} ')

    bookings = TelehealthBookings.query.filter(
        TelehealthBookings.payment_notified == False,  # prevent multiple notifications for one appointment
        TelehealthBookings.status == 'Accepted'  # can only be charged if accepted, if accepted late will be caught
    ).filter(
        or_(  # booking either today, tomorrow or the next day
            and_(  # if next day, either less or more than 48 hours away and must check for that
                TelehealthBookings.target_date_utc == target_time.date(),
                TelehealthBookings.booking_window_id_start_time_utc <= target_time_window
            ),
            or_(  # check for bookings that slipped past celery somehow
                # better safe than sorry, better late than never
                TelehealthBookings.target_date_utc == middle_dt.date(),
                TelehealthBookings.target_date_utc == time_now.date()
            )
        )).all()

    for booking in bookings:
        logger.info(f'Upcoming booking that will be charge in about 24 hours detected with id {booking.idx}')
        upcoming_booking_payment_notification.delay(booking.idx)

    logger.info(f'upcoming booking charges periodic task for {time_now} completed')


celery.conf.beat_schedule = {
    # look for upcoming appointments:
    'check-for-upcoming-bookings': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_tasks',
        'schedule': crontab(minute='*/10')
    },
    # temporary member cleanup
    'cleanup_temporary_care_team': {
        'task': 'odyssey.tasks.periodic.cleanup_temporary_care_team',
        'schedule': crontab(minute='0', hour='*/1')
    },
    # telehealth appointment charging
    #'find_chargable_bookings': {
    #    'task': 'odyssey.tasks.periodic.find_chargable_bookings',
    #    'schedule': crontab(minute='*/5')
    #},
    # search for telehealth transcripts that need to be stored, deploy those storage tasks
    'appointment_transcript_store_scheduler': {
        'task': 'odyssey.tasks.periodic.deploy_appointment_transcript_store_tasks',
        'schedule': crontab(hour=0, minute=10)
    },
    # practitioner no show
    'detect_practitioner_no_show': {
        'task': 'odyssey.tasks.periodic.detect_practitioner_no_show',
        'schedule': crontab(minute='*/5')
    },
    # dosespot notifications
    'get_dosespot_notifications': {
        'task': 'odyssey.tasks.periodic.get_dosespot_notifications',
        'schedule': crontab(hour=1, minute=0)
    },
    'update_active_subscriptions': {
        'task': 'odyssey.tasks.periodic.deploy_subscription_update_tasks',
        'args': (60,),
        'schedule': crontab(minute='*/60')
    },
    # availability
    'remove_expired_availability_exceptions': {
        'task': 'odyssey.tasks.periodic.remove_expired_availability_exceptions',
        'schedule': crontab(hour='0', minute='0')
    },
    # scheduled maintenances
    'create_subtasks_to_notify_clients_and_staff_of_imminent_scheduled_maintenance': {
        'task': 'odyssey.tasks.periodic.create_subtasks_to_notify_clients_and_staff_of_imminent_scheduled_maintenance',
        'schedule': crontab(minute='*/15')
    }
    # upcoming booking payment to be charged
    #'check_for_upcoming_booking_charges': {
    #    'task': 'odyssey.tasks.periodic.check_for_upcoming_booking_charges',
    #    'schedule': crontab(minute='*/6')  # if this were just 30 it would be run at the same time as other periodics
    #    # off setting this slightly might theoretically smooth out the load on celery
    #}
}
