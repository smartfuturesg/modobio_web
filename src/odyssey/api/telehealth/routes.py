import os, boto3, secrets, pathlib
from datetime import datetime, time, timedelta
from dateutil import tz
import random
import requests
import json

from flask import request, current_app, g
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
from sqlalchemy import select
from sqlalchemy.sql.expression import and_, or_
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant, ChatGrant

from odyssey import db
from odyssey.api.lookup.models import (
    LookupBookingTimeIncrements
)
from odyssey.api.staff.models import StaffOperationalTerritories, StaffCalendarEvents, StaffRoles
from odyssey.api.user.models import User
from odyssey.api.telehealth.models import (
    TelehealthBookingStatus,
    TelehealthBookings,
    TelehealthChatRooms,
    TelehealthMeetingRooms, 
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
    TelehealthBookingDetails,
    TelehealthStaffSettings
)
from odyssey.api.telehealth.schemas import (
    TelehealthBookingsSchema,
    TelehealthBookingsOutputSchema,
    TelehealthBookingMeetingRoomsTokensSchema,
    TelehealthChatRoomAccessSchema,
    TelehealthConversationsNestedSchema, 
    TelehealthMeetingRoomSchema,
    TelehealthQueueClientPoolSchema,
    TelehealthQueueClientPoolOutputSchema,
    TelehealthStaffAvailabilitySchema,
    TelehealthTimeSelectOutputSchema,
    TelehealthStaffAvailabilityOutputSchema,
    TelehealthBookingDetailsSchema,
    TelehealthBookingDetailsGetSchema, 
    TelehealthStaffSettingsSchema,
    TelehealthBookingsPUTSchema,
    TelehealthUserSchema
)
from odyssey.api.system.models import SystemTelehealthSessionCosts
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations
)
from odyssey.api.practitioner.models import PractitionerCredentials
from odyssey.api.payment.models import PaymentMethods, PaymentHistory
from odyssey.utils.auth import token_auth
from odyssey.utils.errors import GenericNotFound, InputError, UnauthorizedUser, ContentNotFound, IllegalSetting, GenericThirdPartyError
# from odyssey.integrations.wheel import Wheel
from odyssey.utils.constants import (
    TELEHEALTH_BOOKING_LEAD_TIME_HRS,
    TWILIO_ACCESS_KEY_TTL,
    DAY_OF_WEEK,
    ALLOWED_AUDIO_TYPES,
    ALLOWED_IMAGE_TYPES,
    IMAGE_MAX_SIZE
) 
from odyssey.utils.message import PushNotification, PushNotificationType
from odyssey.utils.misc import (
    FileHandling,
    check_client_existence, 
    check_staff_existence,
    create_conversation,
    create_twilio_access_token,
    generate_meeting_room_name,
    get_chatroom,
    grab_twilio_credentials
)
from odyssey.utils.base.resources import BaseResource

ns = Namespace('telehealth', description='telehealth bookings management API')

@ns.route('/bookings/meeting-room/access-token/<int:booking_id>/')
class TelehealthBookingsRoomAccessTokenApi(Resource):
    """
    This endpoint is used to GET the staff and client's TWILIO access tokens so they can
    access their chats and videos.

    Here, we create the Booking Meeting Room.

    Call start
    """
    @token_auth.login_required
    @responds(schema=TelehealthBookingMeetingRoomsTokensSchema, api=ns, status_code=200)
    def get(self, booking_id):
        # Get the current user
        current_user, _ = token_auth.current_user()
        
        booking = TelehealthBookings.query.get(booking_id)

        if not booking:
            raise InputError(status_code=405, message='Meeting does not exist yet.')

        # make sure the requester is one of the participants
        if not any(current_user.user_id == uid for uid in [booking.client_user_id, booking.staff_user_id]):
            raise InputError(status_code=405, message='logged in user must be a booking participant')

        # Create telehealth meeting room entry
        # each telehealth session is given a unique meeting room
        meeting_room = db.session.execute(
            select(TelehealthMeetingRooms).
            where(
                TelehealthMeetingRooms.booking_id == booking_id,
                )).scalar()
        
        if not meeting_room:
            meeting_room = TelehealthMeetingRooms(
                booking_id=booking_id,
                staff_user_id=booking.staff_user_id,
                client_user_id=booking.client_user_id)
            meeting_room.room_name = generate_meeting_room_name()

        # Create access token for users to access the Twilio API
        # Add grant for video room access using meeting room name just created
        # Twilio will automatically create a new room by this name.
        # TODO: configure meeting room
        # meeting type (group by default), participant limit , callbacks
        
        token = create_twilio_access_token(current_user.modobio_id, meeting_room_name=meeting_room.room_name)
        
        if g.user_type == 'staff':
            meeting_room.staff_access_token = token

            ##
            # If the booking is with a wheel practitioner
            # send a consult start request to wheel
            ##
            # if booking.external_booking_id and False:
            #     wheel = Wheel()
            #     wheel.start_consult(booking.external_booking_id)

        elif g.user_type == 'client':
            meeting_room.client_access_token = token
        
        db.session.add(meeting_room)

        # Create TelehealthBookingStatus object and update booking status to 'In Progress'
        booking.status = 'In Progress'
        status_history = TelehealthBookingStatus(
            booking_id=booking_id,
            reporter_id=current_user.user_id,
            reporter_role='Practitioner' if current_user.user_id == booking.staff_user_id else 'Client',
            status='In Progress'
        )
        db.session.add(status_history)
        db.session.commit() 

        # Send push notification to user, only if this endpoint is accessed by staff.
        # Do this as late as possible, have everything else ready.
        if g.user_type == 'staff':
            pn = PushNotification()

            # TODO: at the moment only Apple is supported. When Android is needed,
            # update PushNotification class and templates, then change here.
            msg = pn.apple_voip_tmpl
            msg['data']['booking_id'] = booking_id
            msg['data']['booking_description'] = 'Modo Bio telehealth appointment'
            msg['data']['staff_id'] = booking.staff_user_id
            msg['data']['staff_first_name'] = booking.practitioner.firstname
            msg['data']['staff_middle_name'] = booking.practitioner.middlename
            msg['data']['staff_last_name'] = booking.practitioner.lastname

            urls = {}
            fh = FileHandling()
            for pic in booking.practitioner.staff_profile.profile_pictures:
                if pic.original:
                    continue

                url = fh.get_presigned_url(pic.image_path)
                urls[pic.height] = url

            msg['data']['staff_profile_picture'] = urls

            pn.send(booking.client_user_id, PushNotificationType.voip, msg)

        return {'twilio_token': token,
                'conversation_sid': booking.chat_room.conversation_sid}

@ns.route('/client/time-select/<int:user_id>/')
@ns.doc(params={'user_id': 'Client user ID'})
class TelehealthClientTimeSelectApi(Resource):   

    @token_auth.login_required
    @responds(schema=TelehealthTimeSelectOutputSchema,api=ns, status_code=200)
    def get(self, user_id):
        """
        Checks the booking requirements stored in the client queue

        Responds with available booking times localized to the client's timezone
        """
        
        #### TESTING NOTES:
        ####   test1 - call with non-existent user_id
        ####   test2 - call with deleted user (user_id exists, but user shouldn't have access to anything)
        ####   test3 - call with staff user_id
        ####   test4 - call with valid client user_id
        check_client_existence(user_id)

        # grab the client at the top of the queue?
        # Need to grab this for to grab the closest target_date / priority date
        # --------------------------------------------------------------------------
        # TODO: client_in_queue, is a list where we are supposed to grab from the top.
        # What if that client does not select a time, how do we move to the next person in the queue
        # client_in_queue MUST be the user_id
        # 
        # --------------------------------------------------------------------------
        #### TESTING NOTES:
        ####   test1 - call existent user_id but not in queue, (code needs an extra check to raise an error when client_in_queue== None) 
        ####   test2 - call with client user_id that might be found in queue
        client_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id).order_by(TelehealthQueueClientPool.priority.desc(),TelehealthQueueClientPool.target_date.asc()).first()
        if not client_in_queue:
            raise InputError(status_code=405,message='Client is not in the queue yet.')
        
        time_inc = LookupBookingTimeIncrements.query.all()
        
        time_idx_dict = {item.start_time.isoformat() : item.idx for item in time_inc} # {datetime.time: booking_availability_id}
        ##
        #  Wheel availability request
        ##
        # wheel = Wheel() 
        #########################

        duration = client_in_queue.duration
        days_from_target = 0
        no_staff_available_count = 0
        times = []

        time_now_utc = datetime.now(tz.UTC)
        time_now_client_localized = time_now_utc.astimezone(tz.gettz(client_in_queue.timezone))

        # window of possible appointment times spans the full target date
        # localize the start and end times to the client's timezone, 
        # NOTE: wheel will respond with availabilities in UTC but will respect the TZ of requested window 
        target_start_datetime_client_local =  datetime.combine(client_in_queue.target_date, time(0, tzinfo=tz.gettz(client_in_queue.timezone)))
        
        # if request was for a time in the past, use the present time + booking lead time window
        if target_start_datetime_client_local < time_now_client_localized:
            target_start_datetime_client_local = time_now_client_localized + timedelta(hours=TELEHEALTH_BOOKING_LEAD_TIME_HRS+1)
            target_start_datetime_client_local = target_start_datetime_client_local.replace(minute=0, second=0, microsecond=0)
        
        while len(times) < 10:
            # convert client's target date to day_of_week
            # 0 is Monday, 6 is Sunday

            # target booking window localized to the client's tzone
            target_start_datetime = target_start_datetime_client_local + timedelta(days_from_target)
            target_end_datetime = target_start_datetime + timedelta(hours=24)
            
            # localize target time range to utc
            target_start_datetime_utc = target_start_datetime.astimezone(tz.UTC)
            target_end_datetime_utc = target_end_datetime.astimezone(tz.UTC)

            # taret time indexes in UTC
            target_start_idx_utc = time_idx_dict[target_start_datetime_utc.strftime('%H:%M:%S')]
            target_end_idx_utc = time_idx_dict[target_end_datetime_utc.strftime('%H:%M:%S')]
            target_start_weekday_utc = DAY_OF_WEEK[target_start_datetime_utc.weekday()]
            target_end_weekday_utc = DAY_OF_WEEK[target_end_datetime_utc.weekday()]

            ######### WHEEL ###########
            # # Query wheel for available practitioners on target date in client's tzone
            # # TODO: when wheel is ready, add sex to this availability check
            
            # wheel_practitioner_availabilities = wheel.openings(
            #     target_time_range = (target_start_datetime_utc, target_end_datetime_utc), 
            #     location_id=client_in_queue.location_id)

            # allow wheel request during testing but, do not add clinician availabilities to response.
            # We only have one wheel sandbox which can get very messy if we include booking wheel test clinicians
            # as part of our test routines.  
            # if current_app.config['TESTING']:
            #     available = {}
            #     staff_availability_timezone = {}
            # else:    
            #     available = wheel_practitioner_availabilities  # availability dictionary {date: {user_id : [booking time idxs]}
            #     staff_availability_timezone =  {_user_id: 'UTC' for _user_id in wheel_practitioner_availabilities} # current tz info for each staff we bring up for this target date
            ######### WHEEL ###########

            available = {}
            staff_availability_timezone = {}

            # gender preference for availability query below
            if client_in_queue.medical_gender == 'm':
                genderFlag = True
            elif client_in_queue.medical_gender == 'f':
                genderFlag = False

            # get 2 letter text abbreviation for operational territory in order to match it with the
            # PractitionerCredentials table
            client_location = LookupTerritoriesOfOperations.query.filter_by(idx=client_in_queue.location_id).one_or_none().sub_territory_abbreviation

            # query staff availabilites filtering by day of week, role, operation location, and gender
            # staff availbilities are stored in UTC time which may be different from the client's tz
            # to handle this case, we make this query knowing that availabilities may span two days 
            if client_in_queue.medical_gender == 'np':
                staff_availability = db.session.query(TelehealthStaffAvailability)\
                    .join(PractitionerCredentials, PractitionerCredentials.user_id == TelehealthStaffAvailability.user_id)\
                        .filter(
                            or_(
                                and_(
                                    TelehealthStaffAvailability.day_of_week == target_start_weekday_utc,
                                    TelehealthStaffAvailability.booking_window_id >= target_start_idx_utc),
                                and_(
                                    TelehealthStaffAvailability.day_of_week == target_end_weekday_utc,
                                    TelehealthStaffAvailability.booking_window_id < target_end_idx_utc))                                
                        ).filter(              
                            PractitionerCredentials.role.has(role=client_in_queue.profession_type), 
                            PractitionerCredentials.state == client_location
                        ).all()
            else:
                staff_availability = db.session.query(TelehealthStaffAvailability)\
                    .join(PractitionerCredentials, PractitionerCredentials.user_id == TelehealthStaffAvailability.user_id)\
                        .join(User, User.user_id==TelehealthStaffAvailability.user_id)\
                        .filter(
                            or_(
                                and_(
                                    TelehealthStaffAvailability.day_of_week == target_start_weekday_utc,
                                    TelehealthStaffAvailability.booking_window_id >= target_start_idx_utc),
                                and_(
                                    TelehealthStaffAvailability.day_of_week == target_end_weekday_utc,
                                    TelehealthStaffAvailability.booking_window_id < target_end_idx_utc))
                        ).filter( 
                                PractitionerCredentials.role.has(role=client_in_queue.profession_type), 
                                PractitionerCredentials.state == client_location,
                                User.biological_sex_male==genderFlag
                        ).all()
            
            if not staff_availability and not available:
                no_staff_available_count+=1
                days_from_target+=1
                if no_staff_available_count >= 7:
                    raise InputError(status_code=404,message='No staff available for the upcoming week.')
                else:
                    # continue jumps the to the top of the loop
                    continue
            else:
                # reset the counter if there is a staff member
                no_staff_available_count = 0
            
            # Duration is taken from the client queue.
            # we divide it by 5 because our look up tables are in increments of 5 mintues
            # so, this represents the number of time blocks we will need to look at.
            # The subtract 1 is due to the indices having start_time and end_times, so 100 - 103 is 100.start_time to 103.end_time which is
            # the 20 minute duration
            idx_delta = int(duration/5) - 1
           
            ###
            # Take all staff availabilities and organize them into a dictionary:
            #       { target_date_utc : {staff_user_id : [booking_increment_ids]} }
            ###
            for availability in staff_availability:
                availability_date = (target_start_datetime_utc.date() if availability.day_of_week == target_start_weekday_utc else target_end_datetime_utc.date())
                staff_user_id = availability.user_id
                if availability_date not in available:
                    available[availability_date] = {}
                if staff_user_id not in available[availability_date]:
                    available[availability_date][staff_user_id] = []
                # NOTE booking_window_id is the actual booking_window_id (starting at 1 NOT 0)
                available[availability_date][staff_user_id].append(availability.booking_window_id)

                if staff_user_id not in staff_availability_timezone:
                    staff_availability_timezone[staff_user_id] = availability.settings.timezone
            ###
            # Bring up current bookings for the target date.
            # Remove booking time blocks from the staff_availability dictionary so we know the times that the staff is free
            # If the client has a booking on the same day, that time block will not be available for another booking. 
            ###
            # search bookings between client's availability window
            bookings = db.session.execute(
                select(TelehealthBookings
                ).where(or_(
                    TelehealthBookings.target_date_utc == target_start_datetime_utc.date(),
                    TelehealthBookings.target_date_utc == target_end_datetime_utc.date())
                ).where(TelehealthBookings.status.in_(('Accepted', 'Pending')))
            ).scalars().all()

            # Now, subtract booking times from staff availability and generate the actual times a staff member is free
            removedNum = {target_start_datetime_utc.date():{}} # {date: {user_id : [booking_ids blocked]}}
            clientBookingID = {target_start_datetime_utc.date(): []}
            if target_start_datetime_utc.date() != target_end_datetime_utc.date():
                removedNum[target_end_datetime_utc.date()] = {} 
                clientBookingID[target_end_datetime_utc.date()]= []

            for booking in bookings:
                staff_id = booking.staff_user_id
                client_id = booking.client_user_id
                if staff_id in available[booking.target_date_utc]:
                    if staff_id not in removedNum[booking.target_date_utc]:
                        removedNum[booking.target_date_utc][staff_id] = []
                    # loop though time increments in booking and remove them from availability
                    # NOTE: booking_window_id_start/end_time are in the staff member's TZ
                    for num in range(booking.booking_window_id_start_time_utc,booking.booking_window_id_end_time_utc+1):
                        if num in available[booking.target_date_utc][staff_id]:
                            available[booking.target_date_utc][staff_id].remove(num)
                            removedNum[booking.target_date_utc][staff_id].append(num)
                        # store client booked times so we dont show these times to the client
                        if client_id == user_id:
                            clientBookingID[booking.target_date_utc].append(num)         
                else:
                    # This staff_user_id should not have availability on this day
                    continue
            # if client is already booked for the target date, remove this time block from all availabilities.  
            for booking_date, booking_timeslots in clientBookingID.items():
                for staff_id in available.get(booking_date,[]):
                    if staff_id not in removedNum[booking_date]:
                        removedNum[booking_date][staff_id] = []
                    available[booking_date][staff_id] = list(set(available[booking_date][staff_id]) - set(booking_timeslots))
                    available[booking_date][staff_id].sort()
                    removedNum[booking_date][staff_id].extend(booking_timeslots)            

            ###
            # Take 5 minute time blocks and convert them into appointment timeslots with a 20-minute duration
            # Loop through available time blocks by target date, staff_id
            # 
            ###

            # NOTE: It might be a good idea to shuffle user_id_arr and only select up to 10 (?) staff members 
            # to reduce the time complexity
            # user_id_arr = [1,2,3,4,5]
            # user_id_arr.random() -> [3,5,2,1,4]
            # user_id_arr[0:3]

            timeArr = {} # client localized booking times, should only be for the target date the client specified 

            for target_date, staff_availability in available.items():
                for staff_id in staff_availability:
                    if staff_id not in removedNum[target_date]:
                        removedNum[target_date][staff_id] = []  

                    # loop through available time blocks
                    #          
                    for idx,time_id in enumerate(available[target_date][staff_id]):  
                        # if not at end of availability list               
                        if idx + idx_delta < len(available[target_date][staff_id]):
                            # If there is a continuous block of time equal to the desired meeting duration
                            if available[target_date][staff_id][idx+idx_delta] - time_id == idx_delta:
                                # since we are accessing an array, we need to -1 because recall time_id is the ACTUAL time increment idx
                                # and arrays are 0 indexed in python
                                # booking start time options should be every 15 mins
                                if time_inc[time_id-1].start_time.minute%15 == 0: 
                                    # client's tz: client_in_queue.timezone
                                    # staff availabilities stored in UTC
                                    start_time_utc = datetime.combine(
                                        target_date, 
                                        time_inc[time_id-1].start_time, 
                                        tzinfo=tz.UTC)
                                    
                                    start_time_client_localized = start_time_utc.astimezone(tz.gettz(client_in_queue.timezone))     

                                    # add this start time to the timeArr dict
                                    if start_time_client_localized not in timeArr:
                                        timeArr[start_time_client_localized] = []

                                    # ensure the staff does not have any overlapping bookings and can fulfill the pre/post booking buffer of 5 mins
                                    # if this staff does not have the time blocks open, do not add them to the timeArr dict
                                    if time_id+idx_delta in removedNum[target_date][staff_id]:
                                        continue                                            
                                    else:                                 
                                        timeArr[start_time_client_localized].append({"staff_id": staff_id,"idx":time_idx_dict[start_time_client_localized.strftime('%H:%M:%S')]})                                                            
                            else:
                                continue
                        else:
                            break 

            ##
            # Loop through timeArr:
            # 1. select one staff member per time block 
            # 2. Localize staff availablility times to client's timezone. Remove any time blocks that 
            #    are target_day - 1 day in the client's tzimezone 
            # note, time.idx NEEDS a -1 in the append, 
            # BECAUSE we are accessing the array where index starts at 0
            ##
            booking_duration_delta = timedelta(minutes=5*(idx_delta+1))
            for _time in timeArr:
                if not timeArr[_time]:
                    continue
                if len(timeArr[_time]) > 1:
                    random.shuffle(timeArr[_time])
                
                end_time_client_localized = _time+booking_duration_delta
                
                # respond with display start and end times for the client
                # and booking window ids which appear as they are in the 
                # TelehealthStaffAvailability table (not localized to the client)
                times.append({'staff_user_id': timeArr[_time][0]['staff_id'],
                            'start_time': _time.time(), 
                            'end_time': end_time_client_localized.time(),
                            'booking_window_id_start_time': timeArr[_time][0]['idx'],
                            'booking_window_id_end_time': timeArr[_time][0]['idx']+idx_delta,
                            'target_date': _time.date()})             

            # increment days_from_target if there are less than 10 times available
            days_from_target+=1

        times.sort(key=lambda t: t['start_time'])    
        times.sort(key=lambda t: t['target_date'])

        payload = {'appointment_times': times,
                   'total_options': len(times)}
        return payload


@ns.route('/bookings/')
class TelehealthBookingsApi(BaseResource):
    """
    This API resource is used to get and post client and staff bookings.
    """     
    @token_auth.login_required
    @responds(schema=TelehealthBookingsOutputSchema, api=ns, status_code=200)
    @ns.doc(params={'client_user_id': 'Client User ID',
                'staff_user_id' : 'Staff User ID',
                'booking_id': 'booking_id'}) 
    def get(self):
        """
        Returns the list of bookings for clients and/or staff
        """
        current_user, _ = token_auth.current_user()

        client_user_id = request.args.get('client_user_id', type=int)

        staff_user_id = request.args.get('staff_user_id', type=int)

        booking_id = request.args.get('booking_id', type=int)

        fh = FileHandling()

        ###
        # There are 5 cases to decide what to return:
        # 1. booking_id is provided: other parameters are ignored, only that booking will be returned to the participating client/staff or any cs
        # 2. No parameter provided: an error will be raised
        # 3. Only staff_user_id provided: all bookings for the staff user will return if loggedin user = staff_user_id or cs
        # 4. Only client_user_id provided: all bookings for the client user will return if loggedin user = client_user_id or cs
        # 5. Both client_user_id and staff_user_id provided: all bookings with both participats return if loggedin user = staff_user_id or client_user_id or cs
        # client_user_id | staff_user_id | booking_id
        #       -        |      -        |      T
        #       F        |      F        |      F      
        #       F        |      T        |      F
        #       T        |      F        |      F
        #       T        |      T        |      F
        ###

        if not (client_user_id or staff_user_id or booking_id):
            # 2. No parameter provided, raise error
            raise InputError(status_code=405,message='Must include at least one of (client_user_id, staff_user_id, booking_id)')
        
        if booking_id:
            # 1. booking_id provided, any other parameter is ignored, only returns booking to participants or cs
            booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
            if not booking:
                raise ContentNotFound() 
            if not any(current_user.user_id == uid for uid in [booking.client_user_id, booking.staff_user_id]) and \
                not ('client_services' in [role.role for role in current_user.roles]):
                raise InputError(status_code=403, message='Logged in user must be a booking participant')
            
            # return booking & both profile pictures 
            bookings = [booking]
            
        elif staff_user_id and not client_user_id:
            # 3. only staff_user_id provided, return all bookings for such user_id if loggedin user is same user or cs
            if not current_user.user_id == staff_user_id and not ('client_services' in [role.role for role in current_user.roles]):
                raise InputError(status_code=403, message='Logged in user must be a booking participant')

            # return all bookings with given staff_user_id
            bookings = TelehealthBookings.query.filter_by(staff_user_id = staff_user_id).\
                order_by(TelehealthBookings.target_date.asc()).all()

        elif client_user_id and not staff_user_id:
            # 4. only client_user_id provided, return all bookings for such user_id if loggedin user is same user or cs
            if not current_user.user_id == client_user_id and not ('client_services' in [role.role for role in current_user.roles]):
                raise InputError(status_code=403, message='Logged in user must be a booking participant')
            
            # return all bookings with given client_user_ide'
            bookings = TelehealthBookings.query.filter_by(client_user_id = client_user_id).\
                order_by(TelehealthBookings.target_date.asc()).all()

        else:
            # 5. both client and user id's are provided, return bookings where both exist if loggedin is either or cs
            if not any(current_user.user_id == uid for uid in [client_user_id, staff_user_id]) and \
                not ('client_services' in [role.role for role in current_user.roles]):
                raise InputError(status_code=403, message='Logged in user must be a booking participant')
            
            # return all bookings with given client and staff user_id combination
            # grab the whole queue
            bookings = TelehealthBookings.query.filter_by(client_user_id = client_user_id, staff_user_id = staff_user_id).\
                order_by(TelehealthBookings.target_date.asc()).all()

        time_inc = LookupBookingTimeIncrements.query.all()
        bookings_payload = []

        for booking in bookings:
            ##
            # localize booking times to the staff and client 
            # bring up profile pics
            ##

            client = {**booking.client.__dict__}
            practitioner = {**booking.practitioner.__dict__}
            

            # bookings stored in staff timezone
            practitioner['timezone'] = booking.staff_timezone
            #return the practioner profile_picture width=128 if the logged in user is the client involved or client services
            if current_user.user_id == booking.client_user_id or ('client_services' in [role.role for role in current_user.roles]):
                image_paths = {pic.width: pic.image_path for pic in booking.practitioner.staff_profile.profile_pictures}
                practitioner['profile_picture'] = (fh.get_presigned_url(image_paths[128]) if image_paths else None)
            

            start_time_utc = datetime.combine(
                    booking.target_date_utc, 
                    time_inc[booking.booking_window_id_start_time_utc-1].start_time,
                    tzinfo=tz.UTC)
                
            end_time_utc = datetime.combine(
                booking.target_date_utc, 
                time_inc[booking.booking_window_id_end_time_utc-1].end_time,
                tzinfo=tz.UTC)
            
            practitioner['start_time_localized'] = start_time_utc.astimezone(tz.gettz(booking.staff_timezone)).time()
            practitioner['end_time_localized'] = end_time_utc.astimezone(tz.gettz(booking.staff_timezone)).time()

            client['timezone'] = booking.client_timezone
            client['start_time_localized'] = start_time_utc.astimezone(tz.gettz(booking.client_timezone)).time()
            client['end_time_localized'] = end_time_utc.astimezone(tz.gettz(booking.client_timezone)).time()
            # return the client profile_picture wdith=128 if the logged in user is the practitioner involved
            if current_user.user_id == booking.staff_user_id:
                image_paths = {pic.width: pic.image_path for pic in booking.client.client_info.profile_pictures}
                client['profile_picture'] = (fh.get_presigned_url(image_paths[128]) if image_paths else None)
            
            bookings_payload.append({
                'booking_id': booking.idx,
                'target_date_utc': booking.target_date_utc,
                'start_time_utc': start_time_utc.time(),
                'status': booking.status,
                'profession_type': booking.profession_type,
                'chat_room': booking.chat_room,
                'client_location_id': booking.client_location_id,
                'payment_method_id': booking.payment_method_id,
                'status_history': booking.status_history,
                'client': client,
                'practitioner': practitioner
            })

        # Sort bookings by time then sort by date
        bookings_payload.sort(key=lambda t: t['start_time_utc'])
        bookings_payload.sort(key=lambda t: t['target_date_utc'])
        
        # create twilio access token with chat grant 
        token = create_twilio_access_token(current_user.modobio_id)
        
        payload = {
            'all_bookings': len(bookings_payload),
            'bookings': bookings_payload,
            'twilio_token': token            
        }
        return payload

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=TelehealthBookingsSchema(only=['booking_window_id_end_time', 'booking_window_id_start_time','target_date']), api=ns)
    @responds(schema=TelehealthBookingsOutputSchema, api=ns, status_code=201)
    @ns.doc(params={'client_user_id': 'Client User ID',
                'staff_user_id' : 'Staff User ID'}) 
    def post(self):
        """
        Add client and staff to a TelehealthBookings table.

        Request body includes date and time localized to the client

        Responds with successful booking and conversation_id 
        """
        current_user, _ = token_auth.current_user()

        # Do not allow bookings between days
        if request.parsed_obj.booking_window_id_start_time >= request.parsed_obj.booking_window_id_end_time:
            raise InputError(status_code=405,message='Start time must be before end time.')
        
        client_user_id = request.args.get('client_user_id', type=int)
        
        if not client_user_id:
            raise InputError(status_code=405,message='Missing Client ID')

        staff_user_id = request.args.get('staff_user_id', type=int)
        
        if not staff_user_id:
            raise InputError(status_code=405,message='Missing Staff ID')        
        
        # make sure the requester is one of the participants
        if not any(current_user.user_id == uid for uid in [client_user_id, staff_user_id]):
            raise InputError(status_code=405, message='logged in user must be a booking participant')

        # Check client existence
        super().check_user(client_user_id, user_type='client')
        
        # Check staff existence
        super().check_user(staff_user_id, user_type='staff')

        time_inc = LookupBookingTimeIncrements.query.all()
        start_time_idx_dict = {item.start_time.isoformat() : item.idx for item in time_inc} # {datetime.time: booking_availability_id}
        # bring up client queue details
        client_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=client_user_id).one_or_none()
        if not client_in_queue:
            raise InputError(message="client not yet in queue")

        # Localize the requested booking date and time to UTC
        duration_idx = request.parsed_obj.booking_window_id_end_time - request.parsed_obj.booking_window_id_start_time
        target_start_datetime_utc = datetime.combine(
                                request.parsed_obj.target_date, 
                                time_inc[request.parsed_obj.booking_window_id_start_time-1].start_time, 
                                tzinfo=tz.gettz(client_in_queue.timezone)).astimezone(tz.UTC)
        target_end_datetime_utc = target_start_datetime_utc + timedelta(minutes=5*(duration_idx+1))
        target_start_time_idx_utc = start_time_idx_dict[target_start_datetime_utc.strftime('%H:%M:%S')]
        target_end_time_idx_utc = target_start_time_idx_utc + duration_idx
       
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
                if target_start_time_idx_utc >= booking.booking_window_id_start_time_utc and\
                    target_start_time_idx_utc < booking.booking_window_id_end_time_utc:
                    raise InputError(status_code=405,message='Client {} already has an appointment for this time.'.format(client_user_id))
                elif target_end_time_idx_utc > booking.booking_window_id_start_time_utc and\
                    target_end_time_idx_utc < booking.booking_window_id_end_time_utc:
                    raise InputError(status_code=405,message='Client {} already has an appointment for this time.'.format(client_user_id))

        if staff_bookings:
            for booking in staff_bookings:
                if target_start_time_idx_utc >= booking.booking_window_id_start_time_utc and\
                    target_start_time_idx_utc < booking.booking_window_id_end_time_utc:
                    raise InputError(status_code=405,message='Staff {} already has an appointment for this time.'.format(staff_user_id))
                elif target_end_time_idx_utc > booking.booking_window_id_start_time_utc and\
                    target_end_time_idx_utc < booking.booking_window_id_end_time_utc:
                    raise InputError(status_code=405,message='Staff {} already has an appointment for this time.'.format(staff_user_id))        

        ##
        # ensure staff still has the same availability
        # if staff is a wheel clinician, query wheel for their current availability
        ##
        ########### WHEEL #########
        # wheel = Wheel()
        # wheel_clinician_ids = wheel.clinician_ids(key='user_id') 

        if False: #staff_user_id in wheel_clinician_ids:
            staff_availability = wheel.openings(
                target_time_range = (target_start_datetime_utc-timedelta(minutes=5), target_end_datetime_utc+timedelta(minutes=5)), 
                location_id = client_in_queue.location_id,
                clinician_id=wheel_clinician_ids[staff_user_id])[target_start_datetime_utc.date()].get(staff_user_id)
        else:
            staff_availability = db.session.execute(
                select(TelehealthStaffAvailability).
                filter(
                    TelehealthStaffAvailability.booking_window_id.in_(
                        [target_start_time_idx_utc,target_end_time_idx_utc]),
                    TelehealthStaffAvailability.day_of_week == DAY_OF_WEEK[target_start_datetime_utc.weekday()],
                    TelehealthStaffAvailability.user_id == staff_user_id
                    )
            ).scalars().all()

        if not staff_availability:
            raise InputError(message="Staff does not currently have this time available")

        # staff and client may proceed with scheduling the booking, create the booking and response object
        request.parsed_obj.client_user_id = client_user_id
        request.parsed_obj.staff_user_id = staff_user_id

        # Add staff and client timezones to the TelehealthBooking entry
        staff_settings = db.session.execute(select(TelehealthStaffSettings).where(TelehealthStaffSettings.user_id == staff_user_id)).scalar_one_or_none()
        
        # TODO: set a notification for the staff member so they know to update their settings
        if not staff_settings:
            staff_settings = TelehealthStaffSettings(timezone='UTC', auto_confirm = False, user_id = staff_user_id)
            db.session.add(staff_settings)

        request.parsed_obj.staff_timezone = staff_settings.timezone
        request.parsed_obj.client_timezone = client_in_queue.timezone

        # save client's location for booking
        request.parsed_obj.client_location_id = client_in_queue.location_id

        # save client's payment method
        request.parsed_obj.payment_method_id = client_in_queue.payment_method_id

        # save profession type requested
        request.parsed_obj.profession_type = client_in_queue.profession_type

        # check the practitioner's auto accept setting. 
        if staff_settings.auto_confirm:
            request.parsed_obj.status = 'Accepted'
        else:
            request.parsed_obj.status = 'Pending'
            # TODO: here, we need to send some sort of notification to the staff member letting
            # them know they have a booking request.

        
        # find target date and booking window ids in UTC
        request.parsed_obj.booking_window_id_start_time_utc = target_start_time_idx_utc
        request.parsed_obj.booking_window_id_end_time_utc = target_end_time_idx_utc
        request.parsed_obj.target_date_utc = target_start_datetime_utc.date()
        
        # find start and end time localized to client's timezone
        # convert start, end time and target date from utc star times found above
        if request.parsed_obj.client_timezone != 'UTC':
            start_time_client_localized = target_start_datetime_utc.astimezone(tz.gettz(request.parsed_obj.client_timezone)).time()
            end_time_client_localized = target_end_datetime_utc.astimezone(tz.gettz(request.parsed_obj.client_timezone)).time()
        else:
            start_time_client_localized = target_start_datetime_utc.time()
            end_time_client_localized = target_end_datetime_utc.time()
        
        # consultation rate to booking
        consult_rate = StaffRoles.query.filter_by(user_id=staff_user_id,role=client_in_queue.profession_type).one_or_none().consult_rate
        
        telehealth_meeting_time = timedelta(minutes=5*(duration_idx+1))

        # Calculate time for display:
        # consulte_rate is in hours
        # 30 minutes -> 0.5*consult_rate
        # 60 minutes -> 1*consulte_rate
        # 90 minutes -> 1.5*consulte_rate
        rate = consult_rate*(telehealth_meeting_time)/timedelta(minutes=60)
        
        request.parsed_obj.consult_rate = rate


        db.session.add(request.parsed_obj)
        db.session.flush()


        # if the staff memebr is a wheel clinician, make booking request to wheel API
        booking_url = None
        ######### WHEEL ##########
        # if staff_user_id in wheel_clinician_ids:
        #     external_booking_id, booking_url = wheel.make_booking_request(staff_user_id, client_user_id, client_in_queue.location_id, request.parsed_obj.idx, target_start_datetime_utc)
        #     request.parsed_obj.external_booking_id = external_booking_id

        # create TelehealthBookingStatus object
        status_history = TelehealthBookingStatus(
            booking_id = request.parsed_obj.idx,
            reporter_id = current_user.user_id,
            reporter_role = 'Practitioner' if current_user.user_id == staff_user_id else 'Client',
            status = request.parsed_obj.status
        )
        # save TelehealthBookingStatus object connected to this booking.
        db.session.add(status_history)
        db.session.flush()

        # create Twilio conversation and store details in TelehealthChatrooms table
        create_conversation(staff_user_id = staff_user_id,
                            client_user_id = client_user_id,
                            booking_id=request.parsed_obj.idx)

        # create access token with chat grant for newly provisioned room
        token = create_twilio_access_token(current_user.modobio_id)

        # Once the booking has been successful, delete the client from the queue
        if client_in_queue:
            db.session.delete(client_in_queue)
            db.session.flush()
     
        ##
        # Populate staff calendar with booking
        # localize to staff timezone first
        ##
        if staff_settings.timezone != 'UTC':
            booking_start_staff_localized = target_start_datetime_utc.astimezone(tz.gettz(staff_settings.timezone))
            booking_end_staff_localized = target_end_datetime_utc.astimezone(tz.gettz(staff_settings.timezone))
        else:
            booking_start_staff_localized = target_start_datetime_utc
            booking_end_staff_localized = target_end_datetime_utc

        add_to_calendar = StaffCalendarEvents(user_id=request.parsed_obj.staff_user_id,
                                              start_date=booking_start_staff_localized.date(),
                                              end_date=booking_end_staff_localized.date(),
                                              start_time=booking_start_staff_localized.strftime('%H:%M:%S'),
                                              end_time=booking_end_staff_localized.strftime('%H:%M:%S'),
                                              recurring=False,
                                              availability_status='Busy',
                                              location='Telehealth_'+str(request.parsed_obj.idx),
                                              description='',
                                              all_day=False,
                                              timezone = staff_settings.timezone
                                              )
        db.session.add(add_to_calendar)
        db.session.commit()

        booking = TelehealthBookings.query.filter_by(idx=request.parsed_obj.idx).first()
        client = {**booking.client.__dict__}
        client['timezone'] = booking.client_timezone
        client['start_time_localized'] = start_time_client_localized
        client['end_time_localized'] = end_time_client_localized
        practitioner = {**booking.practitioner.__dict__}
        practitioner['timezone'] = booking.staff_timezone
        practitioner['start_time_localized'] = booking_start_staff_localized.time()
        practitioner['end_time_localized'] = booking_end_staff_localized.time()

        payload = {
            'all_bookings': 1,
            'twilio_token': token,
            'bookings':[
                {
                'booking_id': booking.idx,
                'target_date': booking.target_date,
                'start_time': practitioner['start_time_localized'],
                'status': booking.status,
                'profession_type': booking.profession_type,
                'chat_room': booking.chat_room,
                'client_location_id': booking.client_location_id,
                'payment_method_id': booking.payment_method_id,
                'status_history': booking.status_history,
                'client': client,
                'practitioner': practitioner,
                'booking_url': booking_url
                }
            ] 
        }
        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthBookingsPUTSchema(only=['status', 'payment_method_id']), api=ns)
    @responds(status_code=201,api=ns)
    @ns.doc(params={'booking_id': 'booking_id'}) 
    def put(self):
        """
        PUT request can be used to update the booking STATUS and payment_method
        """
        current_user, _ = token_auth.current_user()
        booking_id = request.args.get('booking_id', type=int)

        # Check if booking exists
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if not booking:
            raise InputError(status_code=405,message='Could not find booking.')
        
        # Verify loggedin user is part of booking
        if not any(current_user.user_id == uid for uid in [booking.client_user_id, booking.staff_user_id]):
            raise InputError(status_code=403, message='Logged in user must be a booking participant')

        data = request.get_json()

        payment_id = data.get('payment_method_id')
        # If user wants to change the payment method for booking
        if payment_id: 
            # Verify it's the client that's trying to change the payment method
            if not current_user.user_id == booking.client_user_id:
                raise InputError(403, 'Only Client may update Payment Method')     
            # Verify payment method idx is valid from PaymentMethods
            # and that the payment method chosen is registered under the client_user_id
            if not PaymentMethods.query.filter_by(user_id=booking.client_user_id, idx=payment_id).one_or_none():
                raise InputError(403, 'Invalid Payment Method')

        new_status = data.get('status')
        if new_status:
            # Can't update status to 'In Progress' through this endpoint
            # only practitioner can change status from pending to accepted
            # both client and practitioner can change status to canceled and completed
            if new_status == 'In Progress':
                raise InputError(405, 'Can only update to this status on Call Start')
            elif new_status in ('Pending', 'Accepted') and current_user.user_id != booking.staff_user_id:
                raise InputError(403, 'Only Practitioner may update to this status')
            
            ##### WHEEL #####    
            # if new_status == 'Canceled' and booking.external_booking_id:
            #     # cancel appointment on wheel system if the staff memebr is a wheel practitioner
            #     wheel = Wheel()
            #     wheel.cancel_booking(booking.external_booking_id)
                
            # Create TelehealthBookingStatus object if the request is updating the status
            status_history = TelehealthBookingStatus(
                booking_id = booking_id,
                reporter_id = current_user.user_id,
                reporter_role = 'Practitioner' if current_user.user_id == booking.staff_user_id else 'Client',
                status = new_status
            )
            db.session.add(status_history)


        booking.update(data)

        # If the booking gets updated for cancelation, then delete it in the Staff's calendar
        if new_status == 'Canceled':
            staff_event = StaffCalendarEvents.query.filter_by(location='Telehealth_{}'.format(booking_id)).one_or_none()
            if staff_event:
                db.session.delete(staff_event)
        
        db.session.commit()

        return 201

    @token_auth.login_required()
    @accepts(schema=TelehealthBookingsSchema, api=ns)
    @responds(status_code=201,api=ns)
    @ns.deprecated
    def delete(self, user_id):
        '''
        DEPRECATED 6.9.21 - Use PUT request to update booking status
        This DELETE request is used to delete bookings. However, this table should also serve as a 
        a log of bookings, so it is up to the Backened team to use this with caution.
        '''
        if request.parsed_obj.booking_window_id_start_time >= request.parsed_obj.booking_window_id_end_time:
            raise InputError(status_code=405,message='Start time must be before end time.')

        client_user_id = request.args.get('client_user_id', type=int)
        
        if not client_user_id:
            raise InputError(status_code=405,message='Missing Client ID')

        staff_user_id = request.args.get('staff_user_id', type=int)
        
        if not staff_user_id:
            raise InputError(status_code=405,message='Missing Staff ID')        
        
        # Check client existence
        check_client_existence(client_user_id)
        
        # Check staff existence
        check_staff_existence(staff_user_id)

        # Check if staff and client have those times open
        bookings = TelehealthBookings.query.filter_by(client_user_id=client_user_id,\
                                                        staff_user_id=staff_user_id,\
                                                        target_date=request.parsed_obj.target_date,\
                                                        booking_window_id_start_time=request.parsed_obj.booking_window_id_start_time).one_or_none()
        
        if not bookings:
            raise InputError(status_code=405,message='Could not find booking for Client {} and Staff {}.'.format(client_user_id, staff_user_id))

        db.session.delete(bookings)
        db.session.commit()

        return 201

@ns.route('/meeting-room/new/<int:user_id>/')
@ns.deprecated
@ns.doc(params={'user_id': 'User ID number'})
class ProvisionMeetingRooms(Resource):
    @token_auth.login_required(user_type=('staff',))
    @responds(schema = TelehealthMeetingRoomSchema, status_code=201, api=ns)
    def post(self, user_id):
        """
        Deprecated 4.15.21

        Create a new meeting room between the logged-in staff member
        and the client specified in the url param, user_id
        """
        check_client_existence(user_id)

        staff_user, _ = token_auth.current_user()

        # Create telehealth meeting room entry
        # each telehealth session is given a unique meeting room
        meeting_room = TelehealthMeetingRooms(staff_user_id=staff_user.user_id, client_user_id=user_id)
        meeting_room.room_name = generate_meeting_room_name()
        

        # Bring up chat room session. Chat rooms are intended to be between a client and staff
        # member and persist through all telehealth interactions between the two. 
        # only one chat room will exist between each client-staff pair
        # If this is the first telehealth interaction between 
        # the client and staff member, a room will be provisioned. 

        twilio_credentials = grab_twilio_credentials()

        # get_chatroom helper function will take care of creating or bringing forward 
        # previously created chat room and add user as a participant using their modobio_id
        conversation = get_chatroom(staff_user_id = staff_user.user_id,
                            client_user_id = user_id,
                            participant_modobio_id = staff_user.modobio_id)


        # Create access token for users to access the Twilio API
        # Add grant for video room access using meeting room name just created
        # Twilio will automatically create a new room by this name.
        # TODO: configure meeting room
        # meeting type (group by default), participant limit , callbacks
        
        token = AccessToken(twilio_credentials['account_sid'], 
                            twilio_credentials['api_key'], 
                            twilio_credentials['api_key_secret'],
                            identity=staff_user.modobio_id, 
                            ttl=TWILIO_ACCESS_KEY_TTL)
        
        token.add_grant(VideoGrant(room=meeting_room.room_name))
        token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))
        
        meeting_room.staff_access_token = token.to_jwt()
        meeting_room.__dict__['access_token'] = meeting_room.staff_access_token
        meeting_room.__dict__['conversation_sid'] = conversation.sid

        db.session.add(meeting_room)
        db.session.commit() 
        return meeting_room

@ns.route('/meeting-room/access-token/<int:room_id>/')
@ns.deprecated
@ns.doc(params={'room_id': 'room ID number'})
class GrantMeetingRoomAccess(Resource):
    """
    For generating and retrieving meeting room access tokens
    """
    @token_auth.login_required
    @responds(schema = TelehealthMeetingRoomSchema, status_code=201, api=ns)
    def post(self, room_id):
        """
        Generate a new Twilio access token with a grant for the meeting room id provided.
        Tokens also have a grant for the chat room between the two participants in 
        the chat room. 

        Users may only be granted access if they are one of the two participants.
        """
        client_user, _ = token_auth.current_user()

        meeting_room = TelehealthMeetingRooms.query.filter_by(client_user_id=client_user.user_id, room_id=room_id).one_or_none()
        if not meeting_room:
            raise GenericNotFound(message="no meeting room found")
        elif meeting_room.client_user_id != client_user.user_id:
            raise UnauthorizedUser(message='user not part of chat room')

        twilio_credentials = grab_twilio_credentials()

        # get_chatroom helper function will take care of creating or bringing forward 
        # previously created chat room and add user as a participant using their modobio_id
        conversation = get_chatroom(staff_user_id = meeting_room.staff_user_id,
                                    client_user_id = client_user.user_id,
                                    participant_modobio_id = client_user.modobio_id)

        # API access for the staff user to specifically access this chat room
        token = AccessToken(twilio_credentials['account_sid'], twilio_credentials['api_key'], twilio_credentials['api_key_secret'],
                         identity=client_user.modobio_id, ttl=TWILIO_ACCESS_KEY_TTL)
        token.add_grant(VideoGrant(room=meeting_room.room_name))
        token.add_grant(ChatGrant(service_sid=conversation.chat_service_sid))

        meeting_room.client_access_token = token.to_jwt()
        meeting_room.__dict__['access_token'] = meeting_room.client_access_token
        meeting_room.__dict__['conversation_sid'] = conversation.sid
        db.session.commit() 
        
        return meeting_room

@ns.route('/meeting-room/status/<int:room_id>/')
@ns.doc(params={'room_id': 'Room ID number'})
class MeetingRoomStatusAPI(Resource):
    """
    Update and check meeting room status
    """
    def post(self):
        """
        For status callback directly from twilio
        
        TODO:

        - authorize access to this API from twilio automated callback
        - check callback reason (we just want the status updated)
        - update meeting status
            - open
            - close
        - use TelehealthMeetingRooms table
        """
    
    @token_auth.login_required
    @responds(schema = TelehealthMeetingRoomSchema, status_code=200, api=ns)
    def get(self, room_id):
        """
        Check the meeting status

        should just return vital details on meeting rooms
        """
        meeting_room = TelehealthMeetingRooms.query.filter_by(room_id=room_id).one_or_none()
        return meeting_room

@ns.route('/settings/staff/availability/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID for a staff'})
class TelehealthSettingsStaffAvailabilityApi(Resource):
    """
    This API resource is used to get, post the staff's general availability
    """
    @token_auth.login_required
    @responds(schema=TelehealthStaffAvailabilityOutputSchema, api=ns, status_code=200)
    def get(self,user_id):
        """
        Returns the staff availability

        This should be for FE usage. 

        Opposite of the POST request, the table stores this table as:
        user_id, day_of_week, booking_window_id
        1, 'Monday', 2
        1, 'Monday', 3
        1, 'Monday', 4
        1, 'Monday', 5
        1, 'Monday', 10
        1, 'Monday', 11
        1, 'Monday', 12

        So, now we have to convert booking_window_id back to human understandable time
        and return the payload:

        availability: [{'day_of_week': str, 'start_time': Time, 'end_time': Time}]        

        """
        # grab staff availability
        check_staff_existence(user_id)
        # Grab the staff's availability and sorted by booking_window_id AND day_of_week
        # Both of the sorts are necessary for this conversion
        availability = TelehealthStaffAvailability.query.filter_by(user_id=user_id).\
                        order_by(TelehealthStaffAvailability.day_of_week.asc(),TelehealthStaffAvailability.booking_window_id.asc()).all()
        
        if not availability:
            return 204
        # timezones for all availability entries will be the same
        # return tzone and auto-confirm from TelehealthStaffSettings table
        tzone = availability[0].settings.timezone
        auto_confirm = availability[0].settings.auto_confirm
        
        # pull the static booking window ids
        booking_increments = LookupBookingTimeIncrements.query.all()

        monArr = []
        tueArr = [] 
        wedArr = []
        thuArr = [] 
        friArr = [] 
        satArr = []
        sunArr = []

        monArrIdx = []
        tueArrIdx = []
        wedArrIdx = []
        thuArrIdx = []
        friArrIdx = []
        satArrIdx = []
        sunArrIdx = []                                                

        # Reorder to be Monday - Sunday

        orderedArr = {}
        orderedArr['Monday'] = []
        orderedArr['Tuesday'] = []
        orderedArr['Wednesday'] = []
        orderedArr['Thursday'] = []
        orderedArr['Friday'] = []
        orderedArr['Saturday'] = []
        orderedArr['Sunday'] = []
        daySwitch = 0

        for time in availability:
            # Get the current day we are iterating through
            currDay = time.day_of_week

            # Day switch and reference day are necessary to know when the day switches.
            if daySwitch == 0:
                refDay = time.day_of_week 
                daySwitch = 1
            # If the day switches, then that indicates to store the last index for the day
            # Then it updates the refDay
            if currDay != refDay:
                end_time = booking_increments[idx2].end_time
                orderedArr[refDay].append({'day_of_week':refDay,'start_time': start_time, 'end_time': end_time})
                daySwitch = 0

            # This next block of code is copy paste for Monday - Sunday.
            if time.day_of_week == 'Monday':                
                # If this is the first time entering this day, then the first index will be used
                # to store the start_time
                if len(monArrIdx) == 0:
                    idx1 = time.booking_window_id - 1
                    start_time = booking_increments[idx1].start_time
                else:
                    # This is the 2+ iteration through this block
                    # now, idx2 should be greater than idx1 because idx1 was stored in the 
                    # previous iteration
                    idx2 = time.booking_window_id - 1
                    # If idx2 - idx1 > 1, then that indicates a gap in time.
                    # If a gap exists, then we store the end_time, and update the start_time.
                    # EXAMPLE: 
                    # Monday Availability ID's: 1,2,3,4,5,6,7,8,9,10,11,12,   24,25,26,27,28
                    # So it will look like:
                    # [{'day_of_week':'Monday, 'start_time': id1.start_time, 'end_time': id12.end_time},
                    # {'day_of_week':'Monday, 'start_time': id24.start_time, 'end_time': id28.end_time}]
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    # We "slide" idx1 up to where idx2 is, so idx1 should always lag idx2
                    idx1 = idx2

                monArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Tuesday':
                if len(tueArrIdx) == 0:
                    idx1 = time.booking_window_id - 1
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id - 1
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                tueArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Wednesday':
                if len(wedArrIdx) == 0:
                    idx1 = time.booking_window_id - 1
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id - 1
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                wedArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Thursday':
                if len(thuArrIdx) == 0:
                    idx1 = time.booking_window_id - 1
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id - 1
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                thuArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Friday':
                if len(friArrIdx) == 0:
                    idx1 = time.booking_window_id  - 1
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id - 1
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                friArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Saturday':
                if len(satArrIdx) == 0:
                    idx1 = time.booking_window_id - 1
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id - 1
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                satArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Sunday':
                if len(sunArrIdx) == 0:
                    idx1 = time.booking_window_id - 1
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id - 1
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                sunArrIdx.append(time.booking_window_id)

        # This is take the very last day and set the final end_time
        end_time = booking_increments[idx2].end_time
        orderedArr[refDay].append({'day_of_week':refDay,'start_time': start_time, 'end_time': end_time})            

        # Store info in to respective days
        monArr = orderedArr['Monday']
        tueArr = orderedArr['Tuesday']
        wedArr = orderedArr['Wednesday']
        thuArr = orderedArr['Thursday']
        friArr = orderedArr['Friday']
        satArr = orderedArr['Saturday']
        sunArr = orderedArr['Sunday']
        
        orderedArray = []
        # Unload ordered array in to a super array
        orderedArray = [*monArr, *tueArr, *wedArr, *thuArr, *friArr, *satArr, *sunArr]

        payload = {'settings': {'timezone': tzone, 'auto_confirm': auto_confirm}}
        payload['availability'] = orderedArray
        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthStaffAvailabilityOutputSchema, api=ns)
    @responds(api=ns, status_code=201) 
    def post(self,user_id):
        """
        Posts the staff availability

        The input schema is supposed to look like: 

        availability: [{'day_of_week': str, 'start_time': Time, 'end_time': Time}]
        Note, availability is an array of json objects.

        However, we store this information in the database as user_id, day_of_week, booking_window_id
        where booking_window_id is in increments of 5 minutes. 

        AKA, we have to convert availability to booking_window_id

        Example:
        user_id, day_of_week, booking_window_id
        1, 'Monday', 2
        1, 'Monday', 3
        1, 'Monday', 4
        1, 'Monday', 5
        1, 'Monday', 10
        1, 'Monday', 11
        1, 'Monday', 12
        """
        # Detect if the staff exists
        check_staff_existence(user_id)
        # grab the static list of booking window id's
        booking_increments = LookupBookingTimeIncrements.query.all()

        ######### WHEEL #########
        # prevent wheel clinicians from submitting telehealth availability
        # wheel = Wheel()
        # wheel_clinician_ids = wheel.clinician_ids(key='user_id') 
        # if user_id in wheel_clinician_ids and request.parsed_obj['availability']:
        #     raise InputError(message = "This practitioner may only edit their telehealth settings. Not availability")

        # Get the staff's availability
        availability = TelehealthStaffAvailability.query.filter_by(user_id=user_id).all()
        # If the staff already has information in it, delete it, and take the new payload as
        # truth. (This was requested by FE)
        if availability:
            for time in availability:
                db.session.delete(time)

        # To conform to FE request
        # If the staff already has information in telehealthStaffStettings, delete it and take new payload as truth
        settings_query = TelehealthStaffSettings.query.filter_by(user_id=user_id).one_or_none()
        if settings_query: 
            db.session.delete(settings_query)

        # Create an idx dictionary array
        availabilityIdxArr = {}
        availabilityIdxArr['Monday'] = []
        availabilityIdxArr['Tuesday'] = []
        availabilityIdxArr['Wednesday'] = []
        availabilityIdxArr['Thursday'] = []
        availabilityIdxArr['Friday'] = []
        availabilityIdxArr['Saturday'] = []
        availabilityIdxArr['Sunday'] = []

        if request.parsed_obj['availability']:
            avail = request.parsed_obj['availability']
            
            if not request.parsed_obj['settings']:  
                raise InputError(400, 'Missing required field settings')
            # Update tzone and auto-confirm in telehealth staff settings table once
            settings_data = request.parsed_obj['settings']
            settings_data.user_id = user_id
            db.session.add(settings_data)

            data = {'user_id': user_id}

            # Loop through the input payload of start_time and end_times
            for time in avail:
                # end time must be after start time
                if time['start_time'] > time['end_time']:
                    db.session.rollback()
                    #TODO: allow availabilities between days 
                    raise InputError(status_code=405,message='Start Time must be before End Time')
                
                # This for loop loops through the booking increments to find where the 
                # start_time input value is equal to booking increment start time index
                # And same with ending idx.
                startIdx = None
                endIdx = None
                for inc in booking_increments:
                    if time['start_time'] == inc.start_time:
                        # notice, booking_increment idx starts at 1, so python indices should be 
                        # 1 less.
                        # startIdx = inc.idx - 1
                        startIdx = inc.idx
                    elif(time['end_time'] == inc.end_time):
                        endIdx = inc.idx
                    # Break out of the for loop when startIdx and endIdx are no longer None
                    if startIdx is not None and \
                        endIdx is not None:
                        break
                # Now, you loop through to store the booking window id in to TelehealthStaffAvailability
                # table.
                for idx in range(startIdx,endIdx+1):
                    if idx not in availabilityIdxArr[time['day_of_week']]:
                        availabilityIdxArr[time['day_of_week']].append(idx)
                        data['booking_window_id'] = idx
                        data['day_of_week'] = time['day_of_week']
                        data_in = TelehealthStaffAvailabilitySchema().load(data)
                        db.session.add(data_in)
                    else:
                        continue

        db.session.commit()
        return 201

@ns.route('/queue/client-pool/')
class TelehealthGetQueueClientPoolApi(Resource):
    """
    This API resource is used to get all the users in the queue.
    """
    @token_auth.login_required
    @responds(schema=TelehealthQueueClientPoolOutputSchema, api=ns, status_code=200)
    def get(self):
        """
        Returns the list of notifications for the given user_id
        """
        # grab the whole queue
        queue = TelehealthQueueClientPool.query.order_by(TelehealthQueueClientPool.priority.desc(),TelehealthQueueClientPool.target_date.asc()).all()
        
        # sort the queue based on target date and priority
        payload = {'queue': queue,
                   'total_queue': len(queue)}

        return payload

@ns.route('/queue/client-pool/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID'})
class TelehealthQueueClientPoolApi(Resource):
    """
    This API resource is used to get, post, and delete the users in the queue.
    """
    @token_auth.login_required
    @responds(schema=TelehealthQueueClientPoolOutputSchema, api=ns, status_code=200)
    def get(self,user_id):
        """
        Returns queue details for the given user_id
        """
        # grab the whole queue
        queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id).order_by(TelehealthQueueClientPool.priority.desc(),TelehealthQueueClientPool.target_date.asc()).all()
        
        # sort the queue based on target date and priority
        payload = {'queue': queue,
                   'total_queue': len(queue)}

        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthQueueClientPoolSchema, api=ns)
    @responds(api=ns, status_code=201)
    def post(self,user_id):
        """
        Add a client to the queue
        """
        check_client_existence(user_id)

        # Client can only have one appointment on one day:
        # GOOD: Appointment 1 Day 1, Appointment 2 Day 2
        # BAD: Appointment 1 Day 1, Appointment 2 Day 1
        appointment_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id).one_or_none()

        if appointment_in_queue:
            db.session.delete(appointment_in_queue)
            db.session.flush()
        
        # Verify location_id is valid
        location_id = request.parsed_obj.location_id
        location = LookupTerritoriesOfOperations.query.filter_by(idx=location_id).one_or_none()
        if not location:
            raise GenericNotFound(f"No location exists with id {location_id}")
        
        # Verify payment method idx is valid from PaymentMethods
        # and that the payment method chosen has the user_id
        payment_id = request.parsed_obj.payment_method_id
        verified_payment_method = PaymentMethods.query.filter_by(user_id=user_id, idx=payment_id).one_or_none()
        if not verified_payment_method:
            raise InputError(403, "Invalid Payment Method")

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()   

        return 200

    @token_auth.login_required()
    @accepts(schema=TelehealthQueueClientPoolSchema, api=ns)
    def delete(self, user_id):
        #Search for user by user_id in User table
        check_client_existence(user_id)
        appointment_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id,target_date=request.parsed_obj.target_date,profession_type=request.parsed_obj.profession_type).one_or_none()
        if appointment_in_queue:
            db.session.delete(appointment_in_queue)
            db.session.commit()
        else:
            raise InputError(status_code=405,message='User {} does not have that date to delete'.format(user_id))

        return 200

@ns.route('/bookings/details/<int:booking_id>')
class TelehealthBookingDetailsApi(Resource):
    """
    This API resource is used to get, post, and delete additional details about a telehealth boooking.
    Details may include a text description, images or voice recordings
    """
    @token_auth.login_required
    @responds(schema=TelehealthBookingDetailsGetSchema, api=ns, status_code=200)
    def get(self, booking_id):
        """
        Returns a list of details about the specified booking_id
        """
        #Check booking_id exists
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if booking is None:
            raise ContentNotFound

        #verify user trying to access details is the client or staff involved in scheulded booking
        # TODO allow access to Client Services?
        if booking.client_user_id != token_auth.current_user()[0].user_id \
            and booking.staff_user_id != token_auth.current_user()[0].user_id:

            raise UnauthorizedUser(message='Only the client or staff member that belong to this booking can view its details')

        res = {'details': None,
                'images': [],
                'voice': None}
        
        #if there aren't any details saved for the booking_id, GET will return empty
        booking = TelehealthBookingDetails.query.filter_by(booking_id = booking_id).first()
        if not booking:
            raise InputError(204, message=f'No details exist for booking id {booking_id}')
        res['details'] = booking.details

        #retrieve all files associated with this booking id
        fh = FileHandling()
        
        prefix = f'meeting_files/id{booking_id:05d}/'
        res['voice'] = fh.get_presigned_urls(prefix=prefix + 'voice')
        res['images'] = fh.get_presigned_urls(prefix=prefix + 'image')
        
        return res
    
    @token_auth.login_required
    @responds(schema=TelehealthBookingDetailsSchema, api=ns, status_code=200)
    def put(self, booking_id):
        """
        Updates telehealth booking details for a specific db entry, filtered by idx
        Edits one file for another, or can edit text details

        Expects form_data: (will ignore anything else)

        Parameters
        ----------
        image : list(file) (optional)
            Image file(s), up to 3 can be send.
        voice : file (optional)
            Audio file, only 1 can be send.
        details : str (optional)
            Further details.
        """
        #verify the editor of details is the client or staff from schedulded booking
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()

        #only the client involved with the booking should be allowed to edit details
        if not booking or booking.client_user_id != token_auth.current_user()[0].user_id:
            raise UnauthorizedUser(message='Only the client of this booking is allowed to edit details')
        
        #verify the booking_id returns a query result
        query = TelehealthBookingDetails.query.filter_by(booking_id=booking_id).one_or_none()
        if not query:
            raise ContentNotFound

        files = request.files #ImmutableMultiDict of key : FileStorage object

        #verify there's something to submit, if nothing, raise input error
        #if (not request.form.get('details') and len(files) == 0):
        if not 'details' in request.form and not 'images' in request.files and not 'voice' in request.files:
            raise InputError(204, message='Nothing to submit')

        #if 'details' is present in form, details will be updated to new string value of details
        #if 'details' is not present, details will not be affected
        if request.form.get('details'):
            query.details = request.form.get('details')

        #if 'images' and 'voice' are both not present, no changes will be made to the current media file
        #if 'images' or 'voice' are present, but empty, the current media file(s) for that category will be removed
        if files:
            fh = FileHandling()
        
            #if images key is present, delete existing images
            if 'images' in files:
                fh.delete_from_s3(prefix=f'meeting_files/id{booking_id:05d}/image')

            #if voice key is present, delete existing recording
            if 'voice' in files:
                fh.delete_from_s3(prefix=f'meeting_files/id{booking_id:05d}/voice')

            hex_token = secrets.token_hex(4)

            #upload images from request to s3
            for i, img in enumerate(files.getlist('images')):
                # validate file size - safe threashold (MAX = 10 mb)
                fh.validate_file_size(img, IMAGE_MAX_SIZE)
                # validate file type
                img_extension = fh.validate_file_type(img, ALLOWED_IMAGE_TYPES)

                s3key = f'meeting_files/id{booking_id:05d}/image_{hex_token}_{i}{img_extension}'
                fh.save_file_to_s3(img, s3key)

                #exit loop if this is the 4th picture, as that is the max allowed
                #setup this way to allow us to easily change the allowed number in the future
                if i >= 3:
                    break

            #upload voice recording from request to S3
            for i, recording in enumerate(files.getlist('voice')):
                # validate file size - safe threashold (MAX = 10 mb)
                fh.validate_file_size(recording, IMAGE_MAX_SIZE)
                # validate file type
                recording_extension = fh.validate_file_type(recording, ALLOWED_AUDIO_TYPES)

                s3key = f'meeting_files/id{booking_id:05d}/voice_{hex_token}_{i}{recording_extension}'
                fh.save_file_to_s3(recording, s3key)

                #exit loop if this is the 1st recording, as that is the max allowed
                #setup this way to allow us to easily change the allowed number in the future
                if i >= 1:
                    break

        db.session.commit()
        return query


    @token_auth.login_required
    @responds(schema=TelehealthBookingDetailsSchema, api=ns, status_code=201)
    def post(self, booking_id):
        """
        Adds details to a booking_id
        Accepts multiple image or voice recording files

        Expects form-data (will ignore anything else)
            images : file(s) list of image files, up to 4
            voice : file
            details : str
        """
        form = request.form
        files = request.files

        #Check booking_id exists
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if not booking:
            raise ContentNotFound

        details = TelehealthBookingDetails.query.filter_by(booking_id=booking_id).one_or_none()
        if details:
            raise IllegalSetting(message=f"Details for booking_id {booking_id} already exists. Please use PUT method")

        #only the client involved with the booking should be allowed to edit details
        if booking.client_user_id != token_auth.current_user()[0].user_id:
            raise UnauthorizedUser(message='Only the client of this booking is allowed to edit details')

        #verify there's something to submit, if nothing, raise input error
        if (not form.get('details') and not files):
            raise InputError(204, message='Nothing to submit')
        
        data = TelehealthBookingDetails()

        if form.get('details'):
            data.details = form.get('details')

        data.booking_id = booking_id

        #Saving media files into s3
        if files:
            fh = FileHandling()
            hex_token = secrets.token_hex(4)

            #upload images from request to s3
            for i, img in enumerate(files.getlist('images')):
                # validate file size - safe threashold (MAX = 10 mb)
                fh.validate_file_size(img, IMAGE_MAX_SIZE)
                # validate file type
                img_extension = fh.validate_file_type(img, ALLOWED_IMAGE_TYPES)

                s3key = f'meeting_files/id{booking_id:05d}/image_{hex_token}_{i}{img_extension}'
                fh.save_file_to_s3(img, s3key)

                #exit loop if this is the 4th picture, as that is the max allowed
                #setup this way to allow us to easily change the allowed number in the future
                if i >= 3:
                    break

            #upload voice recording from request to S3
            for i, recording in enumerate(files.getlist('voice')):
                # validate file size - safe threashold (MAX = 10 mb)
                fh.validate_file_size(recording, IMAGE_MAX_SIZE)
                # validate file type
                recording_extension = fh.validate_file_type(recording, ALLOWED_AUDIO_TYPES)

                s3key = f'meeting_files/id{booking_id:05d}/voice_{hex_token}_{i}{recording_extension}'
                fh.save_file_to_s3(recording, s3key)

                #exit loop if this is the 1st recording, as that is the max allowed
                #setup this way to allow us to easily change the allowed number in the future
                if i >= 1:
                    break

        db.session.add(data)
        db.session.commit()
        return data

    @token_auth.login_required
    @responds(status_code=204)
    def delete(self, booking_id):
        """
        Deletes all booking details entries from db
        """
        #only the client involved with the booking should be allowed to edit details
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if booking is not None and booking.client_user_id != token_auth.current_user()[0].user_id:
            raise UnauthorizedUser(message='Only the client of this booking is allowed to edit details')
        
        details = TelehealthBookingDetails.query.filter_by(booking_id=booking_id).one_or_none()
        if not details:
            raise GenericNotFound(f"No booking details exist for booking id {booking_id}")

        db.session.delete(details)
        db.session.commit()

        #delete s3 resources for this booking id
        fh = FileHandling()
        fh.delete_from_s3(prefix=f'meeting_files/id{booking_id:05d}/')

@ns.route('/chat-room/access-token')
@ns.deprecated
@ns.doc(params={'client_user_id': 'Required. user_id of client participant.',
               'staff_user_id': 'Required. user_id of staff participant'})
class TelehealthChatRoomApi(Resource):
    """
    DEPRECATED 5.10.21

    Creates an access token for the chat room between one staff and one client user.
    Chat rooms persist through the full history of the two users so the chat history (transcript)
    will be preserved by Twilio.  
    """
    @token_auth.login_required()
    @responds(schema=TelehealthChatRoomAccessSchema, status_code=201, api=ns)
    def post(self):
        """
        Creates access token for already provisioned chat rooms. If no chat room exists, 
        one will not be created.

        Parameters
        ----------
        client_user_id : int
            user_id of the client participant of the chat room.

        staff_user_id : int
            user_id of the staff participant of the chat room.
   
        """
        staff_user_id = request.args.get('staff_user_id', type=int)
        client_user_id = request.args.get('client_user_id', type=int)

        # check that logged in user is part of the chat room
        user, _ = token_auth.current_user()

        if not staff_user_id or not client_user_id:
            raise InputError(message="missing either staff or client user_id", status_code=400)
        
        if user.user_id not in (staff_user_id, client_user_id):
            raise UnauthorizedUser(message="user not permitted to access conversation")

        # get_chatroom helper function will take care of creating or bringing forward 
        # previously created chat room and add user as a participant using their modobio_id
        # create_new=False so that a new chatroom is not provisioned. This may change in the future.
        conversation = get_chatroom(staff_user_id = staff_user_id,
                                    client_user_id = client_user_id,
                                    participant_modobio_id = user.modobio_id,
                                    create_new=False)

        # API access for the user to specifically access this chat room
        twilio_credentials = grab_twilio_credentials()
        token = AccessToken(twilio_credentials['account_sid'], 
                            twilio_credentials['api_key'], 
                            twilio_credentials['api_key_secret'],
                            identity=user.modobio_id, 
                            ttl=TWILIO_ACCESS_KEY_TTL)
                            
        token.add_grant(ChatGrant(service_sid=conversation.chat_service_sid))

        payload = {'access_token': token.to_jwt(),
                   'conversation_sid': conversation.sid}

        return payload

@ns.route('/chat-room/access-token/all/<int:user_id>/')
@ns.deprecated
@ns.doc(params={'user_id': 'User ID number'})
class TelehealthAllChatRoomApi(Resource):
    """
    DEPRECATED 5.10.21

    Endpoint for dealing with all conversations a user is a participant to within a certain context (staff or client)
    """
    @token_auth.login_required
    @responds(api=ns, schema = TelehealthConversationsNestedSchema, status_code=200)
    def get(self, user_id):
        """
        Returns all conversations for the user along with a token to access all chat transcripts.

        Conversations will only be displayed for one context or another. Meaning if the user is logged in as staff,
        they will only be returned all conversations in which they are a staff participant of. 
        """
        #check context of log in from token
        user_type = g.get('user_type')
        
        user = g.get('flask_httpauth_user')[0]

        # user requested must be the logged-in user
        if user.user_id != user_id:
            raise InputError(403, message='user requested must be logged in user')

        if user_type == 'client':
            stmt = select(TelehealthChatRooms, User). \
                join(User, User.user_id == TelehealthChatRooms.staff_user_id).\
                where(TelehealthChatRooms.client_user_id==user_id)
            query = db.session.execute(stmt).all()
            conversations = [dict(zip(('conversation','staff_user'), dat)) for dat in query ]
        elif user_type == 'staff':
            stmt = select(TelehealthChatRooms, User). \
                join(User, User.user_id == TelehealthChatRooms.client_user_id).\
                where(TelehealthChatRooms.staff_user_id==user_id)
            query = db.session.execute(stmt).all()
            conversations = [dict(zip(('conversation','client_user'), dat)) for dat in query]
        else:
            raise InputError(403, message='user not authorized')
        

        # add chat grants to a new twilio access token
        twilio_credentials = grab_twilio_credentials()
        token = AccessToken(twilio_credentials['account_sid'], 
                    twilio_credentials['api_key'], 
                    twilio_credentials['api_key_secret'],
                    identity=user.modobio_id, 
                    ttl=TWILIO_ACCESS_KEY_TTL)
        token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))

        # loop through conversations to create payload
        conversations_payload = []
        for conversation in conversations:
            staff_user = conversation.get('staff_user', user)
            client_user = conversation.get('client_user', user)
            conversations_payload.append({
                'conversation_sid': conversation['conversation'].conversation_sid,
                'booking_id': conversation['conversation'].booking_id,
                'staff_user_id': staff_user.user_id,
                'staff_fullname': staff_user.firstname+' '+staff_user.lastname,
                'client_user_id': client_user.user_id,
                'client_fullname': client_user.firstname+' '+client_user.lastname,
            })

        payload = {'conversations' : conversations_payload,
                   'twilio_token': token.to_jwt()}
            
        return payload
        
@ns.route('/bookings/complete/<int:booking_id>/')
class TelehealthBookingsRoomAccessTokenApi(Resource):
    """
    API for completing bookings
    """
    @token_auth.login_required(user_type=('staff',))
    @responds(api=ns, status_code=200)
    def put(self, booking_id):
        """
        Complete the booking by:
        - send booking complete request to wheel
        - update booking status in TelehealthBookings
        """
        booking = db.session.execute(select(TelehealthBookings).where(
            TelehealthBookings.idx == booking_id,
            TelehealthBookings.status == 'In Progress')).scalars().one_or_none()
        if not booking:
            raise InputError(status_code=405, message='Meeting does not exist yet or has not yes begun')

        current_user, _ = token_auth.current_user()

        # make sure the requester is one of the participants
        if not current_user.user_id == booking.staff_user_id:
            raise InputError(status_code=405, message='logged in user must be a booking participant')

        ##### WHEEL #####        
        # if booking.external_booking_id:
        #     wheel = Wheel()
        #     wheel.complete_consult(booking.external_booking_id)
        

        booking.status = 'Completed'

        status_history = TelehealthBookingStatus(
            booking_id=booking_id,
            reporter_id=current_user.user_id,
            reporter_role='Practitioner',
            status='Completed'
        )
        db.session.add(status_history)
        db.session.commit() 

        return 
