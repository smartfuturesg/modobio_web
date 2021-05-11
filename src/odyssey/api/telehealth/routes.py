import os, boto3, secrets, pathlib, io

from flask import request, current_app, g
from flask_accepts import accepts, responds
from flask_restx import Resource
from sqlalchemy import select
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant, ChatGrant
import random
from werkzeug.datastructures import FileStorage

from odyssey import db
from odyssey.api import api

from odyssey.api.lookup.models import (
    LookupBookingTimeIncrements
)
from odyssey.api.staff.models import StaffRoles
from odyssey.api.user.models import User

from odyssey.api.telehealth.models import (
    TelehealthBookings,
    TelehealthChatRooms,
    TelehealthMeetingRooms, 
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
    TelehealthBookingDetails
)
from odyssey.api.telehealth.schemas import (
    TelehealthBookingsSchema,
    TelehealthBookingsOutputSchema,
    TelehealthBookingMeetingRoomsTokensSchema,
    TelehealthBookingsPUTSchema,
    TelehealthChatRoomAccessSchema,
    TelehealthConversationsNestedSchema, 
    TelehealthMeetingRoomSchema,
    TelehealthQueueClientPoolSchema,
    TelehealthQueueClientPoolOutputSchema,
    TelehealthStaffAvailabilitySchema,
    TelehealthTimeSelectOutputSchema,
    TelehealthStaffAvailabilityOutputSchema,
    TelehealthBookingDetailsSchema,
    TelehealthBookingDetailsGetSchema
) 
from odyssey.api.lookup.models import (
    LookupTerritoriesofOperation
)
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import TWILIO_ACCESS_KEY_TTL, DAY_OF_WEEK, ALLOWED_AUDIO_TYPES, ALLOWED_IMAGE_TYPES
from odyssey.utils.errors import GenericNotFound, InputError, LoginNotAuthorized, UnauthorizedUser, ContentNotFound, IllegalSetting
from odyssey.utils.misc import (
    check_client_existence, 
    check_staff_existence,
    create_conversation, 
    generate_meeting_room_name,
    get_chatroom,
    grab_twilio_credentials
)
ns = api.namespace('telehealth', description='telehealth bookings management API')

@ns.route('/bookings/meeting-room/access-token/<int:booking_id>/')
@ns.doc(params={'booking_id':'booking ID'})
class TelehealthBookingsRoomAccessTokenApi(Resource):
    """
    This endpoint is used to GET the staff and client's TWILIO access tokens so they can
    access their chats and videos.

    Here, we create the Booking Meeting Room.
    """
    @token_auth.login_required
    @responds(schema=TelehealthBookingMeetingRoomsTokensSchema,api=ns,status_code=200)
    def get(self,booking_id):
        # Get the current user
        current_user, _ = token_auth.current_user()
        
        booking,chatroom = db.session.execute(
            select(TelehealthBookings,TelehealthChatRooms).
            join(TelehealthChatRooms,TelehealthBookings.idx==TelehealthChatRooms.booking_id).
            where(
                TelehealthBookings.idx == booking_id,
                )).one_or_none()

        if not booking:
            raise InputError(status_code=405,message='Meeting does not exist yet.')

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
            meeting_room = TelehealthMeetingRooms(booking_id=booking_id,staff_user_id=booking.staff_user_id, client_user_id=booking.client_user_id)
            meeting_room.room_name = generate_meeting_room_name()
        
        # Bring up chat room session. Chat rooms are intended to be between a client and staff
        # member and persist through all telehealth interactions between the two. 
        # only one chat room will exist between each client-staff pair
        # If this is the first telehealth interaction between 
        # the client and staff member, a room will be provisioned. 

        twilio_credentials = grab_twilio_credentials()


        # Create access token for users to access the Twilio API
        # Add grant for video room access using meeting room name just created
        # Twilio will automatically create a new room by this name.
        # TODO: configure meeting room
        # meeting type (group by default), participant limit , callbacks
        
        token = AccessToken(twilio_credentials['account_sid'], 
                            twilio_credentials['api_key'], 
                            twilio_credentials['api_key_secret'],
                            identity=current_user.modobio_id, 
                            ttl=TWILIO_ACCESS_KEY_TTL)
        
        token.add_grant(VideoGrant(room=meeting_room.room_name))
        token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))
        token_jwt = token.to_jwt()
        if g.user_type == 'staff':
            meeting_room.staff_access_token = token_jwt
        elif g.user_type == 'client':
            meeting_room.client_access_token = token_jwt

        db.session.add(meeting_room)
        db.session.commit() 
        return {'twilio_token': token_jwt,
                'conversation_sid': chatroom.conversation_sid}

@ns.route('/client/time-select/<int:user_id>/')
@ns.doc(params={'user_id': 'Client user ID'})
class TelehealthClientTimeSelectApi(Resource):                               
    
    @token_auth.login_required
    @responds(schema=TelehealthTimeSelectOutputSchema,api=ns, status_code=200)
    def get(self,user_id):
        """
        Returns the list of available times a staff member is available
        """
        # Check if the client exists

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
        duration = client_in_queue.duration
        # convert client's target date to day_of_week
        target_date = client_in_queue.target_date.date()
        
        # 0 is Monday, 6 is Sunday
        weekday_id = target_date.weekday()
        weekday_str = DAY_OF_WEEK[weekday_id]
        
        # This should return ALL staff available on that given day.
        # TODO, MUST INCLUDE PROFESSION TYPE FILTER, perhaps delete down low

        if client_in_queue.medical_gender == 'm':
            genderFlag = True
        elif client_in_queue.medical_gender == 'f':
            genderFlag = False

        if client_in_queue.medical_gender == 'np':
            staff_availability = db.session.query(TelehealthStaffAvailability)\
                .join(StaffRoles, StaffRoles.user_id==TelehealthStaffAvailability.user_id)\
                    .filter(TelehealthStaffAvailability.day_of_week==weekday_str, StaffRoles.role==client_in_queue.profession_type).all()
        else:
            staff_availability = db.session.query(TelehealthStaffAvailability)\
                .join(StaffRoles, StaffRoles.user_id==TelehealthStaffAvailability.user_id)\
                    .join(User, User.user_id==TelehealthStaffAvailability.user_id)\
                    .filter(TelehealthStaffAvailability.day_of_week==weekday_str, StaffRoles.role==client_in_queue.profession_type,User.biological_sex_male==genderFlag).all()
        #### TESTING NOTES:
        ####   test1 - test with weekday_str when we have 0 availabilities (check if staff_availability is empty)
        
        # TODO if no staff availability do something
        if not staff_availability:
            # If a client makes an appointment for Monday, and no staff are available,
            # So the client updates or wants to check for appointments on Tuesday
            # Without this delete, the Monday day will still be "first" in the client_in_queue query above
            db.session.delete(client_in_queue)
            db.session.commit()
            raise InputError(status_code=405,message='No staff available')
        # Duration is taken from the client queue.
        # we divide it by 5 because our look up tables are in increments of 5 mintues
        # so, this represents the number of time blocks we will need to look at.
        # The subtract 1 is due to the indices having start_time and end_times, so 100 - 103 is 100.start_time to 103.end_time which is
        # the 20 minute duration
        idx_delta = int(duration/5) - 1
        # TODO will need to incorporate timezone information
        available = {}

        staff_user_id_arr = []
        # Loop through all staff that have indicated they are available on that day of the week
        #
        # The expected output is the first and last index of their time blocks, AKA:
        # availability[staff_user_id] = [[100, 120], [145, 160]]
        #

        for availability in staff_availability:
            staff_user_id = availability.user_id
            if staff_user_id not in available:
                available[staff_user_id] = []
                staff_user_id_arr.append(staff_user_id)
            # NOTE booking_window_id is the actual booking_window_id (starting at 1 NOT 0)
            available[staff_user_id].append(availability.booking_window_id)

        # Now, grab all of the bookings for that client and all staff on the given target date
        # This is necessary to subtract from the staff_availability above.
        # If a client or staff cancels, then that time slot is now available
        bookings = TelehealthBookings.query.filter(TelehealthBookings.target_date==target_date,\
                                                   TelehealthBookings.status!='Client Canceled',\
                                                   TelehealthBookings.status!='Staff Canceled').all()
        # Now, subtract booking times from staff availability and generate the actual times a staff member is free
        removedNum = {}
        clientBookingID = []

        for booking in bookings:
            staff_id = booking.staff_user_id
            client_id = booking.client_user_id
            if staff_id in available:
                if staff_id not in removedNum:
                    removedNum[staff_id] = []
                for num in range(booking.booking_window_id_start_time,booking.booking_window_id_end_time+1):
                    if num in available[staff_id]:
                        available[staff_id].remove(num)
                        removedNum[staff_id].append(num)
                    if client_id == user_id:
                        clientBookingID.append(num)         
            else:
                # This staff_user_id should not have availability on this day
                continue

        # This for loop is necessary because if Client 1 already has an appointment:
        # 3pm - 4pm, then NO other staff should offer them a time 3pm - 4pm
        for staff_id in available:
            if staff_id not in removedNum:
                removedNum[staff_id] = []
            available[staff_id] = list(set(available[staff_id]) - set(clientBookingID))
            removedNum[staff_id]+=clientBookingID            
            # for num in clientBookingID:
            #     if num in available[staff_id]:
            #         available[staff_id].remove(num)
            #         removedNum[staff_id].append(num)

        # convert time IDs to actual times for clients to select
        time_inc = LookupBookingTimeIncrements.query.all()
        # NOTE: It might be a good idea to shuffle user_id_arr and only select up to 10 (?) staff members 
        # to reduce the time complexity
        # user_id_arr = [1,2,3,4,5]
        # user_id_arr.random() -> [3,5,2,1,4]
        # user_id_arr[0:3]
        timeArr = {}
        for staff_id in staff_user_id_arr:
            if staff_id not in removedNum:
                removedNum[staff_id] = []            
            for idx,time_id in enumerate(available[staff_id]):                 
                if idx + 1 < len(available[staff_id]):
                    if available[staff_id][idx+1] - time_id < idx_delta and time_id + idx_delta < available[staff_id][-1]:
                        # since we are accessing an array, we need to -1 because recall time_id is the ACTUAL time increment idx
                        # and arrays are 0 indexed in python
                        if time_inc[time_id-1].start_time.minute%15 == 0:
                            if time_inc[time_id-1] not in timeArr:
                                timeArr[time_inc[time_id-1]] = []
                            if time_id+idx_delta in removedNum[staff_id]:
                                continue
                            else:
                                timeArr[time_inc[time_id-1]].append(staff_id)
                    
                    else:
                        continue
                else:
                    continue
        times = []
        # note, time.idx NEEDS a -1 in the append, 
        # BECAUSE we are accessing the array where index starts at 0
        for time in timeArr:
            if not timeArr[time]:
                continue
            if len(timeArr[time]) > 1:
                random.shuffle(timeArr[time])
            
            times.append({'staff_user_id': timeArr[time][0],
                        'start_time': time.start_time, 
                        'end_time': time_inc[time.idx+idx_delta-1].end_time,
                        'booking_window_id_start_time': time.idx,
                        'booking_window_id_end_time': time.idx+idx_delta,
                        'target_date': target_date})             

        times.sort(key=lambda t: t['start_time'])

        payload = {'appointment_times': times,
                   'total_options': len(times)}
        return payload


@ns.route('/bookings/')
@ns.doc(params={'client_user_id': 'Client User ID',
                'staff_user_id' : 'Staff User ID',
                'booking_id': 'booking_id'}) 
class TelehealthBookingsApi(Resource):
    """
    This API resource is used to get and post client and staff bookings.
    """     
    @token_auth.login_required
    @responds(schema=TelehealthBookingsOutputSchema, api=ns, status_code=200)
    def get(self):
        """
        Returns the list of bookings for clients and/or staff
        """
        current_user, _ = token_auth.current_user()

        client_user_id = request.args.get('client_user_id', type=int)

        staff_user_id = request.args.get('staff_user_id', type=int)

        # make sure the requester is one of the participants
        if not any(current_user.user_id == uid for uid in [client_user_id, staff_user_id]):
            raise InputError(status_code=403, message='Logged in user must be a booking participant')
        
        if not client_user_id and not staff_user_id:
            raise InputError(status_code=405,message='Must include at least one staff or client ID.')

        ###
        # There are a few cases. In all the logged-in user must be one of the requested user_ids:
        # 1. Both staff and client IDs part of search. 
        # 2. Only client_id requested, logged-in user has same _user_id and context
        # 3. Only staff_id is requested, logged-in user has same _user_id and context
        # 4. Logged-in user does not fit requested context
        ###
        client_user=None
        staff_user=None
        if client_user_id and staff_user_id:
            # Check client existence
            client_user = check_client_existence(client_user_id)  
            staff_user = check_staff_existence(staff_user_id)

            # grab the whole queue
            query = db.session.execute(
                select(TelehealthBookings, TelehealthChatRooms.conversation_sid).
                join(TelehealthChatRooms, TelehealthBookings.idx == TelehealthChatRooms.booking_id).
                where(
                    TelehealthBookings.client_user_id == client_user_id,
                    TelehealthBookings.staff_user_id == staff_user_id
                    ).
                order_by(TelehealthBookings.target_date.asc())
            ).all()
        
            bookings = [dict(zip(('booking','conversation_sid'), dat)) for dat in query]

        # requesting to view client bookings. Must be logged in as the client
        elif current_user.user_id == client_user_id and g.get('user_type') == 'client':
            # grab this client's bookings
            client_user = current_user
            # bring up booking, set the results in a dictionary
            query = db.session.execute(
                select(TelehealthBookings, TelehealthChatRooms.conversation_sid, User).
                join(TelehealthChatRooms, TelehealthBookings.idx == TelehealthChatRooms.booking_id).
                join(User, User.user_id == TelehealthBookings.staff_user_id).
                where(
                    TelehealthBookings.client_user_id == client_user_id,
                    ).
                order_by(TelehealthBookings.target_date.asc())
            ).all()

            bookings = [dict(zip(('booking','conversation_sid', 'staff_user'), dat)) for dat in query] 
        
        # requesting to view staff bookings. Must be logged in as the staff
        elif current_user.user_id == staff_user_id and g.get('user_type') == 'staff':
            # grab this client's bookings
            staff_user = current_user
            # bring up booking, set the results in a dictionary
            query = db.session.execute(
                select(TelehealthBookings, TelehealthChatRooms.conversation_sid, User).
                join(TelehealthChatRooms, TelehealthBookings.idx == TelehealthChatRooms.booking_id).
                join(User, User.user_id == TelehealthBookings.client_user_id).
                where(
                    TelehealthBookings.staff_user_id == staff_user_id
                    ).
                order_by(TelehealthBookings.target_date.asc())
            ).all()

            bookings = [dict(zip(('booking','conversation_sid', 'client_user'), dat)) for dat in query] 

        else:
            raise InputError(status_code=403, message='Logged in user must be a booking participant')

        time_inc = LookupBookingTimeIncrements.query.all()
        
        bookings_payload = []

        for booking in bookings:
            staff = booking.get('staff_user', staff_user)
            client = booking.get('client_user', client_user)
            book = booking.get('booking')
            bookings_payload.append({
                'booking_id': book.idx,
                'staff_user_id': staff.user_id,
                'client_user_id': client.user_id,
                'staff_first_name': staff.firstname,
                'staff_middle_name': staff.middlename,
                'staff_last_name': staff.lastname,
                'client_first_name': client.firstname,
                'client_middle_name': client.middlename,
                'client_last_name': client.lastname,                
                'start_time': time_inc[book.booking_window_id_start_time-1].start_time,
                'end_time': time_inc[book.booking_window_id_end_time-1].end_time,
                'target_date': book.target_date,
                'status': book.status,
                'profession_type': book.profession_type,
                'conversation_sid': booking.get('conversation_sid')
            })

        # Sort bookings by time then sort by date
        bookings_payload.sort(key=lambda t: t['start_time'])
        bookings_payload.sort(key=lambda t: t['target_date'])

        # create twilio access token with chat grant 
        twilio_credentials = grab_twilio_credentials()
        token = AccessToken(twilio_credentials['account_sid'], 
                    twilio_credentials['api_key'], 
                    twilio_credentials['api_key_secret'],
                    identity=current_user.modobio_id, 
                    ttl=TWILIO_ACCESS_KEY_TTL)
        
        token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))
        
        payload = {
            'all_bookings': len(bookings_payload),
            'bookings': bookings_payload,
            'twilio_token': token.to_jwt()            
        }
        return payload

    @token_auth.login_required()
    @accepts(schema=TelehealthBookingsSchema, api=ns)
    @responds(schema=TelehealthBookingsOutputSchema, api=ns, status_code=201)
    def post(self):
        """
        Add client and staff to a TelehealthBookings table.

        Responds with successful booking and conversation_id 
        """
        current_user, _ = token_auth.current_user()

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
        check_client_existence(client_user_id)
        
        # Check staff existence
        check_staff_existence(staff_user_id)

        # Check if staff and client have those times open
        client_bookings = TelehealthBookings.query.filter_by(client_user_id=client_user_id,target_date=request.parsed_obj.target_date).all()
        staff_bookings = TelehealthBookings.query.filter_by(staff_user_id=staff_user_id,target_date=request.parsed_obj.target_date).all()

        # This checks if the input slots have already been taken.
        if client_bookings:
            for booking in client_bookings:
                if request.parsed_obj.booking_window_id_start_time >= booking.booking_window_id_start_time and\
                    request.parsed_obj.booking_window_id_start_time < booking.booking_window_id_end_time:
                    raise InputError(status_code=405,message='Client {} already has an appointment for this time.'.format(client_user_id))
                elif request.parsed_obj.booking_window_id_end_time > booking.booking_window_id_start_time and\
                    request.parsed_obj.booking_window_id_end_time < booking.booking_window_id_end_time:
                    raise InputError(status_code=405,message='Client {} already has an appointment for this time.'.format(client_user_id))

        if staff_bookings:
            for booking in staff_bookings:
                if request.parsed_obj.booking_window_id_start_time >= booking.booking_window_id_start_time and\
                    request.parsed_obj.booking_window_id_start_time < booking.booking_window_id_end_time:
                    raise InputError(status_code=405,message='Staff {} already has an appointment for this time.'.format(staff_user_id))
                elif request.parsed_obj.booking_window_id_end_time > booking.booking_window_id_start_time and\
                    request.parsed_obj.booking_window_id_end_time < booking.booking_window_id_end_time:
                    raise InputError(status_code=405,message='Staff {} already has an appointment for this time.'.format(staff_user_id))        

        # TODO: we need to add the concept of staff auto accept or not. When we do, we can do a query 
        # to check the staff's auto accept setting. Right now, default it to true.
        staffAutoAccept = True
        if staffAutoAccept:
            request.parsed_obj.status = 'Accepted'
        else:
            request.parsed_obj.status = 'Pending Staff Acceptance'
            # TODO: here, we need to send some sort of notification to the staff member letting
            # them know they have a booking request.

        request.parsed_obj.client_user_id = client_user_id
        request.parsed_obj.staff_user_id = staff_user_id
        db.session.add(request.parsed_obj)
        db.session.flush()

        # create Twilio conversation and store details in TelehealthChatrooms table
        conversation = create_conversation(staff_user_id = staff_user_id,
                            client_user_id = client_user_id,
                            booking_id=request.parsed_obj.idx)

        # create access token with chat grant for newly provisioned room
        twilio_credentials = grab_twilio_credentials()
        token = AccessToken(twilio_credentials['account_sid'], 
                    twilio_credentials['api_key'], 
                    twilio_credentials['api_key_secret'],
                    identity=current_user.modobio_id, 
                    ttl=TWILIO_ACCESS_KEY_TTL)

        token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))

        # Once the booking has been successful, delete the client from the queue
        client_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=client_user_id).one_or_none()

        if client_in_queue:
            db.session.delete(client_in_queue)
            db.session.flush()

        db.session.commit()

        request.parsed_obj.conversation_sid = conversation.sid
        
        payload = {
            'all_bookings': 1,
            'twilio_token': token.to_jwt(),
            'bookings':[request.parsed_obj] 
        }

        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthBookingsSchema, api=ns)
    @responds(status_code=201,api=ns)
    def put(self):
        """
            PUT request should be used purely to update the booking STATUS.
        """
        
        if request.parsed_obj.booking_window_id_start_time >= request.parsed_obj.booking_window_id_end_time:
            raise InputError(status_code=405,message='Start time must be before end time.')


        booking_id = request.args.get('booking_id', type=int)
        
        # Check if staff and client have those times open
        bookings = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()

        if not bookings:
            raise InputError(status_code=405,message='Could not find booking.')

        data = request.get_json()

        bookings.update(data)
        
        db.session.commit()
        return 201

    @token_auth.login_required()
    @accepts(schema=TelehealthBookingsSchema, api=ns)
    @responds(status_code=201,api=ns)
    def delete(self, user_id):
        '''
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
            -authorize access to this API from twilio automated callback
            -check callback reason (we just want the status updated)
            -update meeting status
                -open
                -close
            -use TelehealthMeetingRooms table
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

        payload = {}
        payload['availability'] = orderedArray
        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthStaffAvailabilityOutputSchema, api=ns)
    @responds(schema=TelehealthStaffAvailabilityOutputSchema, api=ns, status_code=201)
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
        # Get the staff's availability
        availability = TelehealthStaffAvailability.query.filter_by(user_id=user_id).all()
        # If the staff already has information in it, delete it, and take the new payload as
        # truth. (This was requested by FE)
        if availability:
            for time in availability:
                db.session.delete(time)

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
            data = {}
            # Loop through the input payload of start_time and end_times
            for time in avail:
                # end time must be after start time
                if time['start_time'] > time['end_time']:
                    db.session.rollback()
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
                        data['user_id'] = user_id
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
    This API resource is used to get, post, and delete the user's in the queue.
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
    This API resource is used to get, post, and delete the user's in the queue.
    """
    @token_auth.login_required
    @responds(schema=TelehealthQueueClientPoolOutputSchema, api=ns, status_code=200)
    def get(self,user_id):
        """
        Returns the list of notifications for the given user_id
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
        if booking.client_user_id != token_auth.current_user()[0].user_id \
            and booking.staff_user_id != token_auth.current_user()[0].user_id:

            raise UnauthorizedUser(message='Only the client or staff member that belong to this booking can view its details')

        res = {'details': None,
                'images': [],
                'voice': None}
        
        #if there aren't any details saved for the booking_id, GET will return empty
        booking = TelehealthBookingDetails.query.filter_by(booking_id = booking_id).first()
        if not booking:
            raise GenericNotFound(f"No booking details exist for the booking with id {booking_id}")

        res['details'] = booking.details
        res['location_id'] = booking.location_id
        location = LookupTerritoriesofOperation.query.filter_by(idx=booking.location_id).one_or_none()
        if not location:
            raise GenericNotFound(f"No location exists with id {location_id}")
        res['location_name'] = location.country + " " + location.sub_territory

        if not current_app.config['LOCAL_CONFIG']:
            #retrieve all files associated with this booking id
            s3prefix = f'meeting_files/id{booking_id:05d}/'
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(current_app.config['S3_BUCKET_NAME'])

            params = {
                'Bucket' : current_app.config['S3_BUCKET_NAME'],
                'Key' : None
            }

            for media in bucket.objects.filter(Prefix=s3prefix):
                params['Key'] = media.key
                url = boto3.client('s3').generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
                if 'voice' in media.key:
                    res['voice'] = url
                else:
                    res['images'] = res['images'] + [url]
        
        return res
    
    @token_auth.login_required()
    @responds(schema=TelehealthBookingDetailsSchema, api=ns, status_code=200)
    def put(self, booking_id):
        """
        Updates telehealth booking details for a specific db entry, filtered by idx
        Edits one file for another, or can edit text details

        Expects form_data: (will ignore anything else)
            image: [files] (list of image files, up to 3 can be sent)
            voice: file (one sound file can be sent)
            details: string

            (optional) : str
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
        if (not request.form.get('details') and len(files) == 0 and not request.form.get('location_id')):
            raise InputError(204, message='Nothing to submit')

        #if 'details' is present in form, details will be updated to new string value of details
        #if 'details' is not present, details will not be affected
        if request.form.get('details'):
            query.details = request.form.get('details')

        #if 'location_id' is present in form, location_id will be updated to new value
        #if 'location_id' is not present, location_id will not be affected
        location_id = request.form.get('location_id')
        if location_id:
            #verify that location id is an int
            #it is provided as a string, so we try to cast as an int to verify
            try:
                int(location_id)
            except:
                raise InputError(422, "Location id must be an integer")

            location = LookupTerritoriesofOperation.query.filter_by(idx=location_id).one_or_none()
            if not location:
                raise GenericNotFound(f"No location exists with id {location_id}")
            query.location_id = location_id

        if not current_app.config['LOCAL_CONFIG']:
            #if 'images' and 'voice' are both not present, no changes will be made to the current media file
            #if 'images' or 'voice' are present, but empty, the current media file(s) for that category will be removed        
            if files:
                s3 = boto3.resource('s3')
                bucket = s3.Bucket(current_app.config['S3_BUCKET_NAME'])

                #used to locate and remove existing files is necessary
                params = {
                    'Bucket': current_app.config['S3_BUCKET_NAME'],
                    'Key': None
                }
        
                #if images key is present, delete existing images
                if 'images' in files:
                    bucket.objects.filter(Prefix=f'meeting_files/id{booking_id:05d}/image').delete()

                #if voice key is present, delete existing recording
                if 'voice' in files:
                    bucket.objects.filter(Prefix=f'meeting_files/id{booking_id:05d}/voice').delete()                     

                MAX_bytes = 524288000 #500 mb
                hex_token = secrets.token_hex(4)

                #add each image supplied to s3 bucket for this meeting
                for i, img in enumerate(files.getlist('images')):
                    #Verifying image size is within a safe threashold (MAX = 500 mb)
                    img.seek(0, os.SEEK_END)
                    img_size = img.tell()
                    if img_size > MAX_bytes:
                        raise InputError(413, 'File too large')

                    #ensure this is not an empty file
                    if img_size > 0:
                        #Rename image (format: 4digitRandomHex_index.img_extension) AND Save=>S3 
                        img_extension = pathlib.Path(img.filename).suffix
                        if img_extension not in ALLOWED_IMAGE_TYPES:
                            raise InputError(422, f'{img_extension} is not an allowed file type. Allowed types are {ALLOWED_IMAGE_TYPES}')

                        img.seek(0)

                        s3key = f'meeting_files/id{booking_id:05d}/image_{hex_token}_{i}{img_extension}'
                        bucket.put_object(Key= s3key, Body=img.stream)

                    #exit loop if this is the 4th picture, as that is the max allowed
                    #setup this way to allow us to easily change the allowed number in the future
                    if i >= 3:
                        break

                #upload new voice file to S3
                for i, recording in enumerate(files.getlist('voice')):
                    #Verifying recording size is within a safe threashold (MAX = 500 mb)
                    recording.seek(0, os.SEEK_END)
                    recording_size = recording.tell()
                    if recording_size > MAX_bytes:
                        raise InputError(413, 'File too large')

                    #ensure this is not an empty file
                    if recording_size > 0:
                        #Rename voice (format: voice_4digitRandomHex_index.img_extension) AND Save=>S3 
                        recording_extension = pathlib.Path(recording.filename).suffix
                        if recording_extension not in ALLOWED_AUDIO_TYPES:
                            raise InputError(422, f'{recording_extension} is not an allowed file type. Allowed types are {ALLOWED_AUDIO_TYPES}')

                        recording.seek(0)

                        s3key = f'meeting_files/id{booking_id:05d}/voice_{hex_token}_{i}{recording_extension}'
                        bucket.put_object(Key= s3key, Body=recording.stream) 

                    #exit loop if this is the 1st recording, as that is the max allowed
                    #setup this way to allow us to easily change the allowed number in the future
                    if i >= 3:
                        break  

        db.session.commit()
        return query


    @token_auth.login_required
    @responds(schema=TelehealthBookingDetailsSchema(many=True), api=ns, status_code=201)
    def post(self, booking_id):
        """
        Adds details to a booking_id
        Accepts multiple image or voice recording files

        Expects form-data (will ignore anything else)
            images : file(s) list of image files, up to 4
            voice : file
            details : str
            location_id (required) : id of the location the client is in
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
        if (not form.get('details') and not form.get('location_id') and not files):
            raise InputError(204, message='Nothing to submit')
        
        payload = []
        data = TelehealthBookingDetails()

        if form.get('details'):
            data.details = form.get('details')

        data.booking_id = booking_id

        #verify that location id is an int
        #it is provided as a string, so we try to cast as an int to verify
        location_id = form.get('location_id')
        try:
            int(location_id)
        except:
            raise InputError(422, "Location id must be an integer")

        location = LookupTerritoriesofOperation.query.filter_by(idx=location_id).one_or_none()
        if not location:
            raise GenericNotFound(f"No location exists with id {location_id}")

        data.location_id = location_id
        
        payload.append(data)

        if not current_app.config['LOCAL_CONFIG']:
            #Saving media files into s3
            if files:
                MAX_bytes = 524288000 #500 mb
                data_list = []
                hex_token = secrets.token_hex(4)

                s3 = boto3.resource('s3')
                bucket = s3.Bucket(current_app.config['S3_BUCKET_NAME'])
            
                #upload images from request to s3
                for i, img in enumerate(files.getlist('images')):
                    #Verifying image size is within a safe threashold (MAX = 500 mb)
                    img.seek(0, os.SEEK_END)
                    img_size = img.tell()
                    if img_size > MAX_bytes:
                        raise InputError(413, 'File too large')

                    #ensure this is not an empty file
                    if img_size > 0:
                        #Rename image (format: 4digitRandomHex_index.img_extension) AND Save=>S3 
                        img_extension = pathlib.Path(img.filename).suffix
                        if img_extension not in ALLOWED_IMAGE_TYPES:
                            raise InputError(422, f'{img_extension} is not an allowed file type. Allowed types are {ALLOWED_IMAGE_TYPES}')

                        img.seek(0)

                        s3key = f'meeting_files/id{booking_id:05d}/image_{hex_token}_{i}{img_extension}'
                        bucket.put_object(Key= s3key, Body=img.stream)

                    #exit loop if this is the 4th picture, as that is the max allowed
                    #setup this way to allow us to easily change the allowed number in the future
                    if i >= 3:
                        break

                #upload voice recording from request to S3
                for i, recording in enumerate(files.getlist('voice')):
                    #Verifying recording size is within a safe threashold (MAX = 500 mb)
                    recording.seek(0, os.SEEK_END)
                    recording_size = recording.tell()
                    if recording_size > MAX_bytes:
                        raise InputError(413, 'File too large')

                    #ensure this is not an empty file
                    if recording_size > 0:
                        #Rename voice (format: voice_4digitRandomHex_index.img_extension) AND Save=>S3 
                        recording_extension = pathlib.Path(recording.filename).suffix
                        if recording_extension not in ALLOWED_AUDIO_TYPES:
                            raise InputError(422, f'{recording_extension} is not an allowed file type. Allowed types are {ALLOWED_AUDIO_TYPES}')

                        recording.seek(0)

                        s3key = f'meeting_files/id{booking_id:05d}/voice_{hex_token}_{i}{recording_extension}'
                        bucket.put_object(Key= s3key, Body=recording.stream)

                    #exit loop if this is the 1st recording, as that is the max allowed
                    #setup this way to allow us to easily change the allowed number in the future
                    if i >= 1:
                        break 

        db.session.add_all(payload)
        db.session.commit()
        return payload

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

        if not current_app.config['LOCAL_CONFIG']:
            #delete s3 resources for this booking id
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(current_app.config['S3_BUCKET_NAME'])
            bucket.objects.filter(Prefix=f'meeting_files/id{booking_id:05d}/').delete()

@ns.route('/chat-room/access-token')
@ns.doc(params={'client_user_id': 'Required. user_id of client participant.',
               'staff_user_id': 'Required. user_id of staff participant'})
class TelehealthChatRoomApi(Resource):
    """
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
@ns.doc(params={'user_id': 'User ID number'})
class TelehealthAllChatRoomApi(Resource):
    """
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
