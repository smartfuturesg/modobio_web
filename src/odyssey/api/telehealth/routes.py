
from flask import request, current_app
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
    TelehealthMeetingRooms, 
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
    TelehealthBookingDetails
)
from odyssey.api.telehealth.schemas import (
    TelehealthBookingsSchema,
    TelehealthBookingsOutputSchema,
    TelehealthChatRoomAccessSchema, 
    TelehealthMeetingRoomSchema,
    TelehealthQueueClientPoolSchema,
    TelehealthQueueClientPoolOutputSchema,
    TelehealthStaffAvailabilitySchema,
    TelehealthTimeSelectOutputSchema,
    TelehealthStaffAvailabilityOutputSchema,
    TelehealthBookingDetailsSchema,
) 
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import TWILIO_ACCESS_KEY_TTL, DAY_OF_WEEK
from odyssey.utils.errors import GenericNotFound, InputError, UnauthorizedUser, ContentNotFound
from odyssey.utils.misc import (
    check_client_existence, 
    check_staff_existence, 
    generate_meeting_room_name,
    get_chatroom,
    grab_twilio_credentials
)
ns = api.namespace('telehealth', description='telehealth bookings management API')

@ns.route('/client/time-select/<int:user_id>/')
@ns.doc(params={'user_id': 'Client user ID'})
class TelehealthClientTimeSelectApi(Resource):                               
    
    @token_auth.login_required
    @responds(schema=TelehealthTimeSelectOutputSchema,api=ns, status_code=201)
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
        # breakpoint()
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
                'staff_user_id' : 'Staff User ID'}) 
class TelehealthBookingsApi(Resource):
    """
    This API resource is used to get and post client and staff bookings.
    """     
    @token_auth.login_required
    @responds(schema=TelehealthBookingsOutputSchema, api=ns, status_code=201)
    def get(self):
        """
        Returns the list of bookings for clients and/or staff
        """

        client_user_id = request.args.get('client_user_id', type=int)

        staff_user_id = request.args.get('staff_user_id', type=int)

        if not client_user_id and not staff_user_id:
            raise InputError(status_code=405,message='Must include at least one staff or client ID.')
        staffOnly = False
        clientOnly = False
        if client_user_id and staff_user_id:
            # Check client existence
            check_client_existence(client_user_id)  
            check_staff_existence(staff_user_id)      
            # grab the whole queue
            booking = TelehealthBookings.query.filter_by(client_user_id=client_user_id,staff_user_id=staff_user_id).order_by(TelehealthBookings.target_date.asc()).all()
        elif client_user_id and not staff_user_id:
            # Check client existence
            check_client_existence(client_user_id)        
            # grab this client's bookings
            booking = db.session.query(TelehealthBookings,User)\
                .join(User, User.user_id == TelehealthBookings.staff_user_id)\
                    .filter(TelehealthBookings.client_user_id == client_user_id)\
                        .all()   
            clientOnly = True     
        elif staff_user_id and not client_user_id:
            # Check staff existence
            check_staff_existence(staff_user_id)        
            # grab this staff member's bookings
            booking = db.session.query(TelehealthBookings,User)\
                .join(User, User.user_id == TelehealthBookings.client_user_id)\
                    .filter(TelehealthBookings.staff_user_id == staff_user_id)\
                        .all()
            staffOnly = True
        time_inc = LookupBookingTimeIncrements.query.all()
        bookings = []

        if staffOnly:
            staff = User.query.filter_by(user_id=staff_user_id).one_or_none()
            for book in booking:
                bookings.append({
                    'booking_id': book[0].idx,
                    'staff_user_id': book[0].staff_user_id,
                    'client_user_id': book[0].client_user_id,
                    'staff_first_name': staff.firstname,
                    'staff_middle_name': staff.middlename,
                    'staff_last_name': staff.lastname,
                    'client_first_name': book[1].firstname,
                    'client_middle_name': book[1].middlename,
                    'client_last_name': book[1].lastname,                
                    'start_time': time_inc[book[0].booking_window_id_start_time-1].start_time,
                    'end_time': time_inc[book[0].booking_window_id_end_time-1].end_time,
                    'target_date': book[0].target_date,
                    'status': book[0].status,
                    'profession_type': book[0].profession_type
                })
        elif clientOnly:
            client = User.query.filter_by(user_id=client_user_id).one_or_none()
            for book in booking:
                bookings.append({
                    'booking_id': book[0].idx,
                    'staff_user_id': book[0].staff_user_id,
                    'client_user_id': book[0].client_user_id,
                    'staff_first_name': book[1].firstname,
                    'staff_middle_name': book[1].middlename,
                    'staff_last_name': book[1].lastname,
                    'client_first_name': client.firstname,
                    'client_middle_name': client.middlename,
                    'client_last_name': client.lastname,                
                    'start_time': time_inc[book[0].booking_window_id_start_time-1].start_time,
                    'end_time': time_inc[book[0].booking_window_id_end_time-1].end_time,
                    'target_date': book[0].target_date,
                    'status': book[0].status,
                    'profession_type': book[0].profession_type
                })
        else:
            staff = User.query.filter_by(user_id=staff_user_id).one_or_none()
            client = User.query.filter_by(user_id=client_user_id).one_or_none()
            for book in booking:
                bookings.append({
                    'booking_id': book.idx,
                    'staff_user_id': book.staff_user_id,
                    'client_user_id': book.client_user_id,
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
                    'profession_type': book.profession_type
                })             
        # Sort bookings by time then sort by date
        bookings.sort(key=lambda t: t['start_time'])
        bookings.sort(key=lambda t: t['target_date'])

        payload = {'bookings': bookings,
                   'all_bookings': len(bookings)}
        
        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthBookingsSchema, api=ns)
    @responds(status_code=201,api=ns)
    def post(self):
        """
            Add client and staff to a TelehealthBookings table.
        """
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
        db.session.commit()
        return 201

    @token_auth.login_required
    @accepts(schema=TelehealthBookingsSchema, api=ns)
    @responds(status_code=201,api=ns)
    def put(self):
        """
            PUT request should be used purely to update the booking STATUS.
        """
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
        token.add_grant(ChatGrant(service_sid=conversation.chat_service_sid))
        
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
@ns.doc(params={'room_id': 'User ID number'})
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
    @responds(schema=TelehealthStaffAvailabilityOutputSchema, api=ns, status_code=201)
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
    def post(self,user_id):
        """
            Add a client to the queue
        """
        check_client_existence(user_id)
        
        # Client can only have one appointment on one day:
        # GOOD: Appointment 1 Day 1, Appointment 2 Day 2
        # BAD: Appointment 1 Day 1, Appointment 2 Day 1
        appointment_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id,target_date=request.parsed_obj.target_date,profession_type=request.parsed_obj.profession_type).one_or_none()

        if not appointment_in_queue:
            request.parsed_obj.user_id = user_id
            db.session.add(request.parsed_obj)
            db.session.commit()
        else:
            raise InputError(status_code=405,message='User {} already has an appointment for this date with this profession type.'.format(user_id))

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
    @responds(schema=TelehealthBookingDetailsSchema(many=True), api=ns, status_code=200)
    def get(self, booking_id):
        """
        Returns a list of details about the specified booking_id
        """
        #Check booking_id exists
        accessing_user = token_auth.current_user()[0]
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if booking is None:
            raise ContentNotFound
        #verify user trying to access details is the client or staff involved in scheulded booking
        if booking.client_user_id != accessing_user.user_id and booking.staff_user_id != accessing_user.user_id:
            raise UnauthorizedUser(message='Not part of booking')
        
        #if there aren't any details saved for the booking_id, GET will return empty
        details = TelehealthBookingDetails.query.filter_by(booking_id = booking_id).all()
        #TODO implement getting presinged link from s3 bucket for each file
        
        return details
    
    @token_auth.login_required()
    @responds(schema=TelehealthBookingDetailsSchema, api=ns, status_code=200)
    def put(self, booking_id):
        """
        Updates telehealth booking details for a specific db entry, filtered by idx
        Edits one file for another, or can edit text details

        Expects form_data: (will ignore anything else)
            idx:(required) int : TelehealthBookingDetails idx
            media(optional) : file**
            **(It will not break if multiple files are sent, but only one will be handled)
            details(optional) : str
        """
        #Validate index is an int and not a zero
        idx = request.form.get('idx', default=0)
        try: idx = int(idx)
        except ValueError: idx = 0

        if idx <= 0:
            raise InputError(204, 'Invalid index')

        #verify the editor of details is the client or staff from schedulded booking
        editor = token_auth.current_user()[0]
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if not booking:
            raise ContentNotFound
        if booking.client_user_id != editor.user_id and booking.staff_user_id != editor.user_id:
            raise UnauthorizedUser(message='Not part of booking')
        
        #verify the booking_id and idx combination return a query result
        query = TelehealthBookingDetails.query.filter_by(booking_id=booking_id, idx=idx).one_or_none()
        if not query:
            raise ContentNotFound

        #if 'details' is present in form, details will be updated to new string value of details
        #if 'details' is not present, details will not be affected
        if type(request.form.get('details')) == str :
            details = request.form.get('details')
            query.details = details

        #if 'media' is not present, no changes will be made to the current media file
        #if 'media' is present, but empty, the current media file will be removed
        #TODO implement editing file in s3 bucket
        if request.files:
            media_file = request.files.get('media')
            query.media = media_file.filename

        db.session.commit()
        return query


    @token_auth.login_required
    @responds(schema=TelehealthBookingDetailsSchema(many=True), api=ns, status_code=201)
    def post(self, booking_id):
        """
        Adds details to a booking_id
        Accepts multiple image or voice recording files

        Expects form-data (will ignore anything else)
            media : file(s)
            details : str
        """
        files = request.files
        form = request.form
        reporter = token_auth.current_user()[0]
        #Check booking_id exists
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if not booking:
            raise ContentNotFound

        #verify the reporter of details is the client or staff from scheulded booking
        if booking.client_user_id != reporter.user_id and booking.staff_user_id != reporter.user_id:
            raise UnauthorizedUser(message='Not part of booking')
        
        #verify there's something to submit, if nothing, raise input error
        if (not form or not form.get('details')) and (not files or not files.get('media')):
            raise InputError(400, message='Nothing to submit')
        
        payload = []
        data = TelehealthBookingDetails()
        #When no files (image or recording) are sent but we get written details add one entry to db 
        if not files or not files.get('media'):
            data.details = form.get('details')
            data.booking_id = booking_id
            payload.append(data)

        #Saving one media file per entry into db
        else:
            media = files.getlist('media')
            for media_file in media:
                #bucket_name = current_app.config['S3_BUCKET_NAME']
                #TODO upload media files to S3 bucket
                data = TelehealthBookingDetails()
                data.details = form.get('details')
                data.booking_id = booking_id
                data.media = media_file.filename
                payload.append(data)

        db.session.add_all(payload)
        db.session.commit()
        return payload

    @token_auth.login_required
    def delete(self, booking_id):
        """
        Deletes all booking details entries from db
        """
        #verify the editor of details is the client or staff from scheulded booking
        editor = token_auth.current_user()[0]
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if booking is not None and booking.client_user_id != editor.user_id and booking.staff_user_id != editor.user_id:
            raise UnauthorizedUser(message='Not part of booking')
        
        #TODO delete files from S3 bucket
        details = TelehealthBookingDetails.query.filter_by(booking_id=booking_id).all()
        for entry in details:
            db.session.delete(entry)
        db.session.commit()
        return f'Deleted all details for booking_id {booking_id}', 200


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

def sortStartTime(val):
    return val['start_time']
