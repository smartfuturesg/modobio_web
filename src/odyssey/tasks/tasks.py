import logging
import secrets

from odyssey.api.payment.models import PaymentMethods

from datetime import datetime, timedelta, time
from io import BytesIO

from flask_migrate import current_app
from sqlalchemy import select

from odyssey import celery, db, mongo
from odyssey.api.client.models import ClientClinicalCareTeam, ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupBookingTimeIncrements, LookupClinicalCareTeamResources
from odyssey.api.notifications.models import Notifications
from odyssey.api.telehealth.models import *
from odyssey.api.user.models import User
from odyssey.integrations.twilio import Twilio
from odyssey.tasks.base import BaseTaskWithRetry
from odyssey.utils.files import FileUpload
from odyssey.utils.telehealth import complete_booking
from odyssey.utils.constants import NOTIFICATION_SEVERITY_TO_ID, NOTIFICATION_TYPE_TO_ID
from odyssey.utils.misc import create_notification, update_client_subscription

logger = logging.getLogger(__name__)

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
              Notifications.notification_type_id == NOTIFICATION_TYPE_TO_ID.get('Scheduling'))
        ).scalars().one_or_none()
    
    existing_client_notification = db.session.execute(
        select(Notifications).
        where(Notifications.user_id == client_user.user_id, 
              Notifications.expires == expires_at, 
              Notifications.notification_type_id == NOTIFICATION_TYPE_TO_ID.get('Scheduling'))
        ).scalars().one_or_none()
    
    # create the staff and client notification entries
    if not existing_staff_notification:

        create_notification(
            booking.staff_user_id, 
            NOTIFICATION_SEVERITY_TO_ID.get('Medium'),
            NOTIFICATION_TYPE_TO_ID.get('Scheduling'),
            f"You have a telehealth appointment at <datetime_utc>{start_dt}</datetime_utc>",
            f"Your telehealth appointment with {client_user.firstname+' '+client_user.lastname} is at <datetime_utc>{start_dt}</datetime_utc>. Please review your client's medical information before taking the call.",
            'Provider',
            expires_at
        )
    
    if not existing_client_notification:

        create_notification(
            booking.client_user_id, 
            NOTIFICATION_SEVERITY_TO_ID.get('Medium'),
            NOTIFICATION_TYPE_TO_ID.get('Scheduling'),
            f"You have a telehealth appointment at <datetime_utc>{start_dt}</datetime_utc>",
            f"Your telehealth appointment with {staff_user.firstname+' '+staff_user.lastname} is at <datetime_utc>{start_dt}</datetime_utc>. Please ensure your medical information is up to date before taking the call.",
            'Client',
            expires_at
        )

    db.session.commit()

    return

@celery.task()
def upcoming_appointment_care_team_permissions(booking_id):
    """
    Apply temporary care team access permissions to the staff member involved in the booking
    """

    # bring up resource_group_ids required for medical doctor visits
    # TODO: update this to align with other staff roles 
    resource_ids_needed = db.session.execute(select(
        LookupClinicalCareTeamResources.resource_id, 
    ).where(LookupClinicalCareTeamResources.access_group.in_(['general','medical_doctor']))).scalars().all()

    # bring up booking
    booking = db.session.execute(select(TelehealthBookings).where(
        TelehealthBookings.idx == booking_id,
        TelehealthBookings.status == 'Accepted')).scalars().one_or_none()

    if not booking:
        return 
    
    # check if staff is already in care team and has permissions
    care_team_staff = db.session.execute(select(ClientClinicalCareTeam
    ).where(
        ClientClinicalCareTeam.user_id==booking.client_user_id,
        ClientClinicalCareTeam.team_member_user_id == booking.staff_user_id)
    ).scalars().one_or_none()

    # the staff member is already part of the user's care team
    # ensure all necessary permissions are applied
    if care_team_staff:
        # bring up current permissions
        current_resource_auths = db.session.execute(select(
            ClientClinicalCareTeamAuthorizations
        ).where(
            ClientClinicalCareTeamAuthorizations.user_id == booking.client_user_id,
            ClientClinicalCareTeamAuthorizations.team_member_user_id == booking.staff_user_id)
        ).scalars().all()

        current_resource_auth_ids = [item.resource_id for item in current_resource_auths if item.status == 'accepted']
        current_resource_auth_ids_not_accepted = [item for item in current_resource_auths if item.status != 'accepted']

        remaining_auths = len(set(resource_ids_needed) - set(current_resource_auth_ids))
        
        # if more resource authorizations are necessary, either add new auths or approve pending auths
        if remaining_auths > 0:
            # approve current pending auths 
            if len(current_resource_auth_ids_not_accepted) > 0:
                for pending_auth in current_resource_auth_ids_not_accepted:
                    pending_auth.status = 'accepted'
                    current_resource_auth_ids.append(pending_auth.resource_id)
                
                remaining_auths = len(set(resource_ids_needed) - set(current_resource_auth_ids))

            # add new permissions
            if remaining_auths > 0:
                for resource_id in remaining_auths:
                    db.session.add(ClientClinicalCareTeamAuthorizations(**{
                        'user_id': booking.client_user_id,
                        'team_member_user_id': booking.staff_user_id,
                        'resource_id': resource_id
                    }))
        # all necessary authorizations already granted
        else:
            return


    # staff not yet part of care team. Add them as a temporary member, assign permissions
    else:
        db.session.add(ClientClinicalCareTeam(**{
            "team_member_user_id": booking.staff_user_id,
            "user_id": booking.client_user_id,
            "is_temporary": True}))

        db.session.commit()

        for resource_id in resource_ids_needed:
            db.session.add(ClientClinicalCareTeamAuthorizations(**{
                'user_id': booking.client_user_id,
                'team_member_user_id': booking.staff_user_id,
                'resource_id': resource_id
            }))
    
    db.session.commit()

    return


#@celery.task()
#def charge_telehealth_appointment(booking_id):
#    """
#    This task will go through the process of attempting to charge a user for a telehealth booking.
#    If the payment is unsuccessful, the booking will be canceled.
#    """
#    # TODO: Notify user of the canceled booking via email? They are already notified via notification
#    booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
#
#    odyssey.integrations.instamed.Instamed().charge_telehealth_booking(booking)
    
@celery.task()
def cancel_noshow_appointment(booking_id):
    """
    This task will cancel a booking in which the practitioner did not show up within 10 minutes of
    the start time. It will then refund the user.
    """
    booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
    booking.status = "Canceled"

    # run the task to store the chat transcript immediately
    if current_app.config['TESTING']:
        #run task directly if in test env
        store_telehealth_transcript(booking.idx)
    else:
        #otherwise run with celery
        store_telehealth_transcript.delay(booking.idx)

    # delete booking from Practitioner's calendar
    staff_event = StaffCalendarEvents.query.filter_by(idx = booking.staff_calendar_id).one_or_none()
    if staff_event:
        db.session.delete(staff_event)

    db.session.commit()
    #odyssey.integrations.instamed.cancel_telehealth_appointment(booking, reason='Practitioner No Show', refund=True)

@celery.task()
def cleanup_unended_call(booking_id: int):
    """ Text """
    completion_info = complete_booking(booking_id)

    return completion_info

@celery.task()
def store_telehealth_transcript(booking_id: int):
    """ Store telehealth transcript in cache.

    Cache the telehealth transcript related to the booking id provided.
    Delete the conversation on twilio's platform once this is acheived. 

    Parameters
    ----------
    booking_id : int
        TelehealthBookings.idx for a booking that has been completed
        and is beyond the telehealth review period. 
    """
    twilio = Twilio()

    # bring up booking
    # For now, the boooking state does not matter. 
    booking = db.session.execute(select(TelehealthBookings
        ).where(TelehealthBookings.idx == booking_id)).scalars().one_or_none()
    
    transcript = twilio.get_booking_transcript(booking.idx)
    payload = {}
    
    if len(transcript) == 0:
        #delete from twilio, nothing to store
        twilio.delete_conversation(booking.chat_room.conversation_sid)
        logger.info(f"Booking ID {booking.idx}: Conversation deleted from twilio.")
        
        #set conversation sid to none since there is nothing to be stored to mongo
        booking.chat_room.conversation_sid = None
    else:
        # if there is media present in the transcript, store it in an s3 bucket
        hex_token = secrets.token_hex(4)
        for message_id, message in enumerate(transcript):
            if message['media']:
                for media_id, media in enumerate(message['media']):
                    # download media from twilio 
                    media_content = twilio.get_media(media['sid'])

                    fu = FileUpload(
                        BytesIO(media_content),
                        booking.client_user_id,
                        prefix=f'telehealth/booking_{booking_id}/message_{message_id}/')
                    fu.validate()
                    fu.save(f'attachment_{hex_token}_{media_id}.{fu.extension}')

                    media['s3_path'] = fu.filename
                    transcript[message_id]['media'][media_id] = media

        payload = {
            'created_at': datetime.utcnow().isoformat(),
            'booking_id': booking.idx,
            'transcript': transcript
        }
        # insert transcript into mongo db under the telehealth_transcripts collection
        if current_app.config['MONGO_URI']:
            _id = mongo.db.telehealth_transcripts.insert_one(payload).inserted_id
            logger.info(f"Booking ID {booking.idx}: Conversation stored on MongoDB with idx {str(_id)}")
        else:
            logger.warning('Mongo db has not been setup. Twilio conversation will not be deleted.')
            _id = None  

        # delete the conversation from twilio if the transcript was successfully stored on mongo
        if _id:
            twilio.delete_conversation(booking.chat_room.conversation_sid)
            logger.info(f"Booking ID {booking.idx}: Conversation deleted from twilio.")
            booking.chat_room.conversation_sid = None
        
        # delete the conversation sid entry, add transcript_object_id from mongodb
        booking.chat_room.transcript_object_id = str(_id)

    db.session.commit()

    if current_app.config['TESTING']:
        return payload
    
    return

@celery.task(base=BaseTaskWithRetry)
def update_client_subscription_task(user_id: int):
    """
    Updates the user's subscription by checking the subscription status with apple. 
    This task is intended to be scheduled right after the current subscription expires.

    Parameters
    ----------
    user_id : int
        used to grab the latest subscription
    """
    
    update_client_subscription(user_id = user_id)

    db.session.commit()
    return


@celery.task(base=BaseTaskWithRetry)
def abandon_telehealth_booking(booking_id: int):
    """
    To be run in the case a client abandons their appointment without explicitly telling us.
    The booking would have only ever been in the Pending status. At this point, only the 
    TelehealthBooking would have been created. No other database entries or resources have been 
    created for the booking. ONly the booking entry needs to be deleted. 

    """

    booking = TelehealthBookings.query.filter_by(idx = booking_id).one_or_none()

    if booking.status == 'Pending':
        TelehealthBookingStatus.query.filter_by(booking_id = booking_id).delete()
        db.session.delete(booking)
        db.session.commit()

@celery.task()
def test_task():
    logger.info("Celery test task succeeded")


@celery.task()
def upcoming_booking_payment_notification(booking_id):
    booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
    payment_method = PaymentMethods.query.filter_by(user_id=booking.client_user_id, is_default=True).one_or_none()
    index = booking.booking_window_id_start_time_utc - 1  # zero the index first
    hours = index / 12
    minutes = (index % 12) * 5
    booking_start_time = time(hour=int(hours), minute=minutes)
    booking_dt_utc = datetime.combine(booking.target_date_utc, booking_start_time)
    create_notification(
        booking.client_user_id,
        NOTIFICATION_SEVERITY_TO_ID.get('Medium'),
        NOTIFICATION_TYPE_TO_ID.get('Payments'),
        "Upcoming Telehealth Charge",
        f"Your payment method ending in {payment_method.number} will be charged for your appointment scheduled on <datetime_utc>{booking_dt_utc}</datetime_utc> in the next 24 hours.",
        "Client",
        booking_dt_utc + timedelta(days=1)  # expiry
    )
    booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
    booking.payment_notified = True
    db.session.commit()  # commits notification add and booking payment_notified setting to true


@celery.task()
def notify_client_of_imminent_scheduled_maintenance(user_id, datum):
    reformed_start = datum['start_time'].replace("T", " ")
    reformed_start = reformed_start[0:19]
    reformed_end = datum['end_time'].replace("T", " ")
    reformed_end = reformed_end[0:19]
    create_notification(
        user_id,
        NOTIFICATION_SEVERITY_TO_ID.get('Highest'),
        NOTIFICATION_TYPE_TO_ID.get('System Maintenance'),
        "System maintenance scheduled",
        f"System maintenance has been scheduled between <datetime_utc>{reformed_start}</datetime_utc> and <datetime_utc>{reformed_end}</datetime_utc>. This means the system will be inaccessible and that it will not be possible to schedule telehealth appointments for that time period.",
        'Client',
        datum['end_time']
    )
    db.session.commit()


@celery.task()
def notify_staff_of_imminent_scheduled_maintenance(user_id, datum):
    reformed_start = datum['start_time'].replace("T", " ")
    reformed_start = reformed_start[0:19]
    reformed_end = datum['end_time'].replace("T", " ")
    reformed_end = reformed_end[0:19]
    create_notification(
        user_id,
        NOTIFICATION_SEVERITY_TO_ID.get('Highest'),
        NOTIFICATION_TYPE_TO_ID.get('System Maintenance'),
        "System maintenance scheduled",
        f"System maintenance has been scheduled between <datetime_utc>{reformed_start}</datetime_utc> and <datetime_utc>{reformed_end}</datetime_utc>. This means the system will be inaccessible and that it will not be possible to accept telehealth bookings for that time period.",
        'Provider',
        datum['end_time']
    )
    db.session.commit()
