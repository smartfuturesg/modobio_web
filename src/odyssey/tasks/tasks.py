import logging
from odyssey.api.user.schemas import UserSubscriptionsSchema

from odyssey.integrations.apple import AppStore
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict
from PIL import Image
from pytz import utc

from bson import ObjectId
from flask_migrate import current_app
from sqlalchemy import select
from werkzeug.datastructures import FileStorage

from odyssey import celery, db, mongo
from odyssey.api.client.models import ClientClinicalCareTeam, ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupBookingTimeIncrements, LookupClinicalCareTeamResources, LookupSubscriptions
from odyssey.api.notifications.models import Notifications
from odyssey.api.telehealth.models import TelehealthBookingStatus, TelehealthBookings
from odyssey.api.user.models import User, UserSubscriptions
from odyssey.integrations.instamed import Instamed, cancel_telehealth_appointment
from odyssey.integrations.twilio import Twilio
from odyssey.tasks.base import BaseTaskWithRetry
from odyssey.utils.files import FileUpload
from odyssey.utils.telehealth import complete_booking

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
              Notifications.notification_type_id == 3)
        ).scalars().one_or_none()
    
    existing_client_notification = db.session.execute(
        select(Notifications).
        where(Notifications.user_id == client_user.user_id, 
              Notifications.expires == expires_at, 
              Notifications.notification_type_id == 3)
        ).scalars().one_or_none()
    
    # create the staff and client notification entries
    if not existing_staff_notification:
        staff_notification = Notifications(
            user_id=booking.staff_user_id,
            title="You have a telehealth appointment in 2 hours",
            content=f"Your telehealth appointment with {client_user.firstname+' '+client_user.lastname} is in 2 hours. Please review your client's medical information before taking the call.",
            expires = expires_at,
            notification_type_id = 3 #Scheduling
        )
        db.session.add(staff_notification)
    
    if not existing_client_notification:
        client_notification = Notifications(
            user_id=booking.client_user_id,
            title="You have a telehealth appointment in 2 hours",
            content=f"Your telehealth appointment with {staff_user.firstname+' '+staff_user.lastname} is in 2 hours. Please ensure your medical information is up to date before taking the call.",
            expires = expires_at,
            notification_type_id = 3 #Scheduling
        )
        db.session.add(client_notification)

    db.session.commit()

    return

@celery.task()
def upcoming_appointment_care_team_permissions(booking_id):
    """
    Apply temporary care team access permissions to the staff member involved in the booking 

    """

    # bring up resouce_group_ids required for medical doctor visits
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

@celery.task()
def process_wheel_webhooks(webhook_payload: Dict[str, Any]):
    """
    TODO: Perform the necessary action depending on the `event` field of the payload
    
    Update the database entry with acknowledgement that the task has been completed
    """
    # bring up the booking in the request
    # if booking does not exist and env != production, skip
    # note, dev mongo db is shared between devlopers, dev environment, and testing environment
    booking = db.session.execute(select(TelehealthBookings
            ).where(TelehealthBookings.external_booking_id == webhook_payload['consult_id'] )).scalars().one_or_none()
    if not booking:
        # possible the request came from another dev instance since our db is not persistent
        if current_app.config['DEV'] or current_app.config['TESTING']:
            mongo.db.wheel.find_one_and_update(
            {"_id": ObjectId(webhook_payload['_id'])}, 
            {"$set":{"modobio_meta.processed":False, "modobio_meta.acknowledged" : True}})
            return
        else:
            # booking somehow was lost in the prod environment, not good
            #TODO: log errors when logger is ready
            return

    ##
    # Handle the webhook request depending on the event field in the payload
    #
    ##

    # sent when clinician recieves notification of the consultation 2-24hrs inadvance. no action
    if webhook_payload['event'] == 'consult.assigned':
        pass

    # consult.unassigned:  consult is canceled on wheel's end, must enact cancellation proceedure
    # clinician.unavailable: the practitioner is no longer available for the booking. treat as a cancellation
    # clinician.no_show: clinician does not enter booking within 10 minutes of their scheduled start time 
    # consult.voided: Sent in rare occasions when wheel clinicians cannot complete the consultation 
    elif webhook_payload['event'] in ('consult.unassigned',  'clinician.no_show', 'clinician.unavailable', 'consult.voided'):
        
        # update booking status to canceled
        booking.status = 'Canceled'

        # create an entry into the TelehealthBookingStatus table
        status_history = TelehealthBookingStatus(
                booking_id = booking.idx,
                reporter_id = booking.staff_user_id,
                reporter_role = 'Practitioner',
                status = 'Canceled'
            )
        db.session.add(status_history)
        
        staff_user = db.session.execute(
            select(User
            ).where(User.user_id == booking.staff_user_id)).scalars().one_or_none()
        
        # add notification to client
        expires_at = datetime.utcnow()+timedelta(days=2)
        client_notification = Notifications(
            user_id=booking.client_user_id,
            title="Your telehealth appointment has been canceled",
            content=f"Your telehealth appointment with {staff_user.firstname+' '+staff_user.lastname} has been canceled. Please reschedule.",
            expires = expires_at,
            notification_type_id = 3 #Scheduling
        )

        db.session.add(client_notification)

        db.session.commit()

    # the practitioner opened the deeplink to the booking and is now reviewing documents
    elif webhook_payload['event'] == 'assignment.accepted':

        # create an entry into the TelehealthBookingStatus table
        status_history = TelehealthBookingStatus(
                booking_id = booking.idx,
                reporter_id = booking.staff_user_id,
                reporter_role = 'Practitioner',
                status = 'Document Review'
            )
        db.session.add(status_history)

        # update booking status to canceled
        booking.status = 'Document Review'

        db.session.commit()
    
    # patient.no_show: patient did not enter booking within 10 minutes of their scheduled start time 
    elif webhook_payload['event'] == 'patient.no_show':

        # update booking status to completed
        booking.status = 'Completed'

        # create an entry into the TelehealthBookingStatus table
        status_history = TelehealthBookingStatus(
                booking_id = booking.idx,
                reporter_id = booking.staff_user_id,
                reporter_role = 'Client',
                status = 'Completed'
            )
        db.session.add(status_history)
        
        staff_user = db.session.execute(
            select(User
            ).where(User.user_id == booking.staff_user_id)).scalars().one_or_none()
            
        # add notification to client
        expires_at = datetime.utcnow()+timedelta(days=2)
        client_notification = Notifications(
            user_id=booking.client_user_id,
            title="Your telehealth appointment has been completed",
            content=f"Your telehealth appointment with {staff_user.firstname+' '+staff_user.lastname} has been completed.",
            expires = expires_at,
            notification_type_id = 3 #Scheduling
        )
        db.session.add(client_notification)

        db.session.commit()
    
    # no event field recognized, should be logged. 
    else:
        return

    # finally, set webhook entry to processed
    if current_app.config['TESTING']:
        return
    else:
        mongo.db.wheel.find_one_and_update(
            {"_id": ObjectId(webhook_payload['_id'])}, 
            {"$set":{"modobio_meta.processed":True, "modobio_meta.acknowledged" :True}})
         
    return

@celery.task()
def charge_telehealth_appointment(booking_id):
    """
    This task will go through the process of attemping to charge a user for a telehealth booking.
    If the payment is unsuccesful, the booking will be canceled.

    TODO: Notify user of the canceled booking via email/notfication
    """
    booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()

    Instamed().charge_user(booking)
    
@celery.task()
def cancel_noshow_appointment(booking_id):
    """
    This task will cancel a booking in which the practitioner did not show up within 10 minutes of
    the start time. It will then refund the user.
    """
    booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
    
    cancel_telehealth_appointment(booking, reason='Practitioner No Show', refund=True)

@celery.task()
def cleanup_unended_call(booking_id: int):

    completion_info = complete_booking(booking_id)

    return completion_info

@celery.task()
def store_telehealth_transcript(booking_id: int):
    """
    Cache the telehealth transcript related to the booking id provided. Delete the conversation on twilio's platform once
    this is acheived. 

    Params
    ------
    booking_id: TelehealthBookings.idx for a booking that has been completed and is beyond the telehealth review period. 
    """
    twilio = Twilio()

    # bring up booking
    # For now, the boooking state does not matter. 
    booking = db.session.execute(select(TelehealthBookings
        ).where(TelehealthBookings.idx == booking_id)).scalars().one_or_none()
    # close conversation so that no more messages can be added to transcript
    twilio.close_telehealth_chatroom(booking.idx)
    
    transcript = twilio.get_booking_transcript(booking.idx)

    # s3 bucket path for the media associated with this booking transcript
    transcript_media_prefix = f'id{booking.client_user_id:05d}/telehealth/{booking_id}/transcript/media'

    # if there is media present in the transcript, store it in an s3 bucket
    media_id = 0
    for idx, message in enumerate(transcript):
        if message['media']:
            for media_idx, media in enumerate(message['media']):
                # download media from twilio 
                media_content = twilio.get_media(media['sid'])

                fu = FileUpload(FileStorage(stream=BytesIO(media_content)))
                fu.validate()
                name = f'{transcript_media_prefix}/{media_id}.{fu.extension}'
                fu.save(name)

                media['s3_path'] = name
                transcript[idx]['media'][media_idx] = media
            
                media_id+=1

    payload = {
        'created_at': datetime.utcnow().isoformat(),
        'booking_id': booking.idx,
        'transcript': transcript
    }
    # insert transcript into mongo db under the telehealth_transcripts collection
    if current_app.config['MONGO_URI']:
        _id = mongo.db.telehealth_transcripts.insert(payload)
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
def update_apple_subscription(user_id:int):
    """
    Updates the user's subscription by checking the subscription status with apple. 
    This task is intended to be scheduled right after the current subscription expires.

    Params
    ------
    user_id: int
        used to grab the latest subscription
    
    """
    
    prev_sub = UserSubscriptions.query.filter_by(user_id=user_id, is_staff=False).order_by(UserSubscriptions.idx.desc()).first()

    # only update the most recent subscription
    if prev_sub.apple_original_transaction_id:
        # if the subscription does not need to be updated, skip update
        if datetime.utcnow() < prev_sub.expire_date:
            return 
        # grab the latest subscription details from Apple
        appstore  = AppStore()
        transaction_info, renewal_info, status = appstore.latest_transaction(prev_sub.apple_original_transaction_id)

        prev_sub.update({'end_date': datetime.fromtimestamp(transaction_info['purchaseDate']/1000, utc).replace(tzinfo=None), 
                        'subscription_status': 'unsubscribed', 
                        'last_checked_date': datetime.utcnow().isoformat()})
        if status not in (1, 3, 4):
            # create entry for unsubscribed status
            new_sub_data = {
                'subscription_status': 'unsubscribed',
                'is_staff': False,
                'start_date':  datetime.utcnow().isoformat()
            }
        else:
            new_sub_data = {
                'subscription_status': 'subscribed',
                'subscription_type_id': LookupSubscriptions.query.filter_by(ios_product_id = transaction_info.get('productId')).one_or_none().sub_id,
                'is_staff': False,
                'apple_original_transaction_id': prev_sub.apple_original_transaction_id,
                'last_checked_date': datetime.utcnow().isoformat(),
                'expire_date': datetime.fromtimestamp(transaction_info['expiresDate']/1000, utc).replace(tzinfo=None).isoformat(),
                'start_date': datetime.fromtimestamp(transaction_info['purchaseDate']/1000, utc).replace(tzinfo=None).isoformat()
            }
        
        new_sub = UserSubscriptionsSchema().load(new_sub_data)
        new_sub.user_id = user_id

        db.session.add(new_sub)

        db.session.commit()

        logger.info(f"Apple subscription updated for user_id: {user_id}")

    return


@celery.task()
def test_task():
    logger.info("Celery test task succeeded")