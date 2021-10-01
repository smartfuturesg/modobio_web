from datetime import datetime, timedelta
from typing import Any, Dict

from bson import ObjectId
from flask_migrate import current_app
from sqlalchemy import select

from odyssey import celery, db, mongo
from odyssey.api.client.models import ClientClinicalCareTeam, ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupBookingTimeIncrements, LookupClinicalCareTeamResources
from odyssey.api.notifications.models import Notifications
from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation
from odyssey.api.telehealth.models import TelehealthBookingStatus, TelehealthBookings
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

    # consult.unassigned:  consult is cancelled on wheel's end, must enact cancellation proceedure
    # clinician.unavailable: the practitioner is no longer available for the booking. treat as a cancellation
    # clinician.no_show: clinician does not enter booking within 10 minutes of their scheduled start time 
    # consult.voided: Sent in rare occasions when wheel clinicians cannot complete the consultation 
    elif webhook_payload['event'] in ('consult.unassigned',  'clinician.no_show', 'clinician.unavailable', 'consult.voided'):
        
        # update booking status to cancelled
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

        # update booking status to cancelled
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