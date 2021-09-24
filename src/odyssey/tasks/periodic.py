from datetime import datetime, date, timedelta, timezone

from celery.schedules import crontab
from celery.signals import worker_ready   
from celery.utils.log import get_task_logger
from sqlalchemy import delete, text
from sqlalchemy import and_, or_, select

from odyssey import celery, db, mongo
from odyssey.tasks.base import BaseTaskWithRetry
from odyssey.tasks.tasks import process_wheel_webhooks, upcoming_appointment_care_team_permissions, upcoming_appointment_notification_2hr
from odyssey.api.telehealth.models import TelehealthBookings
from odyssey.api.client.models import ClientClinicalCareTeamAuthorizations, ClientDataStorage, ClientClinicalCareTeam
from odyssey.api.lookup.models import LookupBookingTimeIncrements
from odyssey.api.notifications.schemas import NotificationSchema
from odyssey.api.payment.models import PaymentFailedTransactions, PaymentMethods
from odyssey.api.system.models import SystemTelehealthSessionCosts
from odyssey.api.user.models import User
from odyssey.utils.constants import INSTAMED_OUTLET

from odyssey.config import Config

logger = get_task_logger(__name__)

# access to the config while running tasks
config = Config()

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
def deploy_upcoming_appointment_tasks(booking_window_id_start, booking_window_id_end, target_date=None):
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
                TelehealthBookings.booking_window_id_start_time_utc >= booking_window_id_start , # ex. 18:00
                or_( #ex  meeting ends between 18:00 and 02:00
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
    if config.TESTING:
        return upcoming_bookings
    
    #schedule pre-appointment tasks
    for booking in upcoming_bookings:
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
        data = {
            'notification_type_id': 14,
            'title': f'{member.firstname} {member.lastname}\'s Data Access Is About To Expire',
            'content': f'Would you like to add {member.firstname} {member.lastname} to your team? Swipe right' + \
                        'on their entry in your team list to make them a permanent member of your team!',
            'action': 'Redirect to team member list',
            'time_to_live': 86400
        }
        new_notificiation = NotificationSchema().load(data)
        new_notificiation.user_id = notification.user_id
        db.session.add(new_notificiation)

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
    This is a persistent background task intended to listen for new entries into the webhook database.
    Each entry represents a webhook request from a third party service. When inserts are detected, this task will 
    deploy a seperate task to handle the webhook request accordingly. 

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
    unprocessed_wheel_wh = mongo.db.wheel.find({ "$or" : [{"modobio_meta.processed":False} , {"modobio_meta.acknowleged" : False}]})

    # send wheel payloads for processing
    for wh_payload in unprocessed_wheel_wh:
        wh_payload['_id'] = str(wh_payload['_id'])
        logger.info("deploying task originating from wheel webhook")
        process_wheel_webhooks.delay(wh_payload)

    # open while loop waits for new inserts to the database from any collection
    while True:
        wh_payload = stream.try_next()
        if wh_payload:
            wh_payload['fullDocument']['_id'] = str(wh_payload['fullDocument']['_id'])
            logger.info(f"deploying task originating from {wh_payload['ns']['coll']} webhook")
            # shoot off background task for each integration accordingly 
            if wh_payload['ns']['coll'] == 'wheel':
                process_wheel_webhooks.delay(wh_payload['fullDocument'])

@worker_ready.connect()
def startup_tasks(**kwargs):
    deploy_webhook_tasks.delay()

@celery.task()
def charge_user_telehealth():
    """
    This task will scan the TelehealthBookings table for appointments that are not yet paid and
    are less than 24 hours away. It will then charge the user for the appointment using the 
    payment method saved to the booking. Unsuccessful charges will be retried up to 6 times in the
    below task.
    """
    
    #get all bookings that are sheduled <24 hours away and have not been charged yet
    target_time = datetime.now(timezone.utc) + timedelta(hours=24)
    target_time_window = LookupBookingTimeIncrements.query                    \
        .filter(LookupBookingTimeIncrements.start_time <= target_time.time(), \
        LookupBookingTimeIncrements.end_time >= target_time.time()).one_or_none()

    bookings = TelehealthBookings.query.filter(TelehealthBookings.charged == False) \
        .filter(or_(
            and_(TelehealthBookings.booking_window_id_start_time_utc <= target_time_window, TelehealthBookings.target_date_utc == datetime.today()),
            and_(TelehealthBookings.booking_window_id_start_time_utc >= target_time_window, TelehealthBookings.target_date_utc == target_time.date())
        )).all()
    
    for booking in bookings:
        payment = PaymentMethods.query.filter_by(idx=booking.payment_method_id)
        session_cost = SystemTelehealthSessionCosts.query.filter_by(profession_type='medical_doctor').one_or_none().session_cost

        request_data = {
            "Outlet": INSTAMED_OUTLET,
            "PaymentMethod": "OnFile",
            "PaymentMethodID": str(payment.payment_id),
            "Amount": str(session_cost)
        }

        request_header = {'Api-Key': current_app.config['INSTAMED_API_KEY'],
                                'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                                'Content-Type': 'application/json'}

        response = requests.post('https://connect.instamed.com/rest/payment/sale',
                        headers=request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            #transaction was not successful, store in PaymentFailedTransactions
            failed = PaymentFailedTransactions(**{
                'user_id': booking.client_user_id,
                'transaction_id': response_data['TransactionID']
            })
            db.session.add(failed)
            db.session.commit()
            booking.charged = True
            return

        #convert response data to json (python dict)
        response_data = json.loads(response.text)

        #check if card was declined (this is not an error as checked above as 200 is returned from InstaMed)
        if response_data['TransactionStatus'] == 'C':
            if response_data['IsPartiallyApproved']:
                #refund partial amount and log as an unsuccessful payment
                request_data = {
                    "Outlet": INSTAMED_OUTLET,
                    "PaymentMethod": "OnFile",
                    "PaymentMethodID": str(payment.payment_id),
                    "Amount": str(response_data['PartialApprovalAmount'])
                }

                request_header = {'Api-Key': current_app.config['INSTAMED_API_KEY'],
                        'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                        'Content-Type': 'application/json'}

                response = requests.post('https://connect.instamed.com/rest/payment/refund',
                                headers=request_header,
                                json=request_data)

                #TODO: log if refund was unsuccessful

                #store in PaymentFailedTransactions
                failed = PaymentFailedTransactions(**{
                    'user_id': booking.client_user_id,
                    'transaction_id': response_data['TransactionID']
                })
                db.session.add(failed)
            else:
                #transaction was successful, store in PaymentHistory
                history = PaymentHistory(**{
                    'user_id': booking.client_user_id,
                    'payment_method_id': booking.payment_method_id,
                    'transaction_id': response_data['TransactionID'],
                    'transaction_amount': session_cost,
                })
                db.session.add(history)
        else:
            #transaction was not successful, store in PaymentFailedTransactions
            failed = PaymentFailedTransactions(**{
                'user_id': booking.client_user_id,
                'transaction_id': response_data['TransactionID']
            })
            db.session.add(failed)

        booking.charged=True

    db.session.commit()

@celery.task()
def charge_unsuccessful_bookings():
    """
    This task will run every hour and will attempt to charge for telehealth bookings that failed
    to be charge by the above task. When an unsuccessful charge has been failed a total of 6 times,
    this task will no longer attempt to charge. Instead, the user will have the unsuccessful charge
    on their account and will be unable to book new appointments until it is resolved.
    """

    transactions = PaymentFailedTransactions.query.filter(PaymentFailedTransactions.retries < 6).all()
    session_cost = SystemTelehealthSessionCosts.query.filter_by(profession_type='medical_doctor').one_or_none().session_cost

    for transaction in transactions:
        #attempt to charge this transaction
        request_data = {
            "Outlet": INSTAMED_OUTLET,
            "PaymentMethod": "OnFile",
            "PaymentMethodID": str(transaction.payment_method.payment_id),
            "Amount": str(session_cost)
        }

        request_header = {'Api-Key': current_app.config['INSTAMED_API_KEY'],
                        'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                        'Content-Type': 'application/json'}

        response = requests.post('https://connect.instamed.com/rest/payment/sale',
                        headers=request_header,
                        json=request_data)

        #check if instamed api raised an error
        try:
            response.raise_for_status()
        except:
            #transaction was not successful, increment attempt count
            transaction.retries += 1
            db.session.commit()
            return

        #convert response data to json (python dict)
        response_data = json.loads(response.text)

        #check if card was declined (this is not an error as checked above as 200 is returned from InstaMed)
        if response_data['TransactionStatus'] == 'C':
            if response_data['IsPartiallyApproved']:
                #refund partial amount and log as an unsuccessful payment
                request_data = {
                    "Outlet": INSTAMED_OUTLET,
                    "PaymentMethod": "OnFile",
                    "PaymentMethodID": str(payment.payment_id),
                    "Amount": str(response_data['PartialApprovalAmount'])
                }

                request_header = {'Api-Key': current_app.config['INSTAMED_API_KEY'],
                        'Api-Secret': current_app.config['INSTAMED_API_SECRET'],
                        'Content-Type': 'application/json'}

                response = requests.post('https://connect.instamed.com/rest/payment/refund',
                                headers=request_header,
                                json=request_data)

                #TODO: log if refund was unsuccessful

                #increment retry count
                transaction.retries += 1
            else:
                #transaction was successful, store in PaymentHistory
                history = PaymentHistory(**{
                    'user_id': booking.client_user_id,
                    'payment_method_id': booking.payment_method_id,
                    'transaction_id': response_data['TransactionID'],
                    'transaction_amount': session_cost,
                })
                db.session.add(history)
                #delete failed payment now that it has been resolved
                db.session.delete(transaction)
        else:
            #transaction was not successful, increment retry count
            transaction.retries += 1

    db.session.commit()

celery.conf.beat_schedule = {
    # refresh the client data storage table every day at midnight
    'add-update-client-data-storage-table': {
        'task': 'odyssey.tasks.periodic.refresh_client_data_storage',
        'schedule': crontab(hour=0, minute=0)
    },
    # look for upcoming apppointment within moving windows:
    # (00:00 - 08:00)
    'check-for-upcoming-bookings-00-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_tasks',
         'args': (1, 96),
        'schedule': crontab(hour=0, minute=0)
    },
    # (06:00 - 14:00)
    'check-for-upcoming-bookings-06-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_tasks',
         'args': (73, 168),
        'schedule': crontab(hour=6, minute=0)
    },
    # (12:00 - 20:00)
    'check-for-upcoming-bookings-12-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_tasks',
         'args': (145, 240),
        'schedule': crontab(hour=12, minute=0)
    },
    # (18:00 - 02:00, Next day)
    'check-for-upcoming-bookings-18-00': {
        'task': 'odyssey.tasks.periodic.deploy_upcoming_appointment_tasks',
         'args': (217, 24),
        'schedule': crontab(hour=18, minute=0)
    },
    #temporary member cleanup
    'cleanup_temporary_care_team': {
        'task': 'odyssey.tasks.periodic.cleanup_temporary_care_team',
        'schedule': crontab(hour=1, minute=0)
    },
    #telehealth appointment charging
    'charge_user_telehealth': {
        'task': 'odyssey.tasks.periodic.charge_user_telehealth',
        'schedule': crontab(hour=0, minute=5)
    },
    #telehealth failed payments
    'charge_unsuccessful_bookings': {
        'task': 'odyssey.tasks.periodic.charge_unsuccessful_bookings',
        'schedule': crontab(hour=1, minute=0)
    }
}
