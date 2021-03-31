
from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
import datetime as dt
import random

from odyssey import db
from odyssey.api import api

from odyssey.api.lookup.models import (
    LookupBookingTimeIncrements
)
from odyssey.api.staff.models import StaffRoles
from odyssey.api.user.models import User

from odyssey.api.staff.models import StaffRoles

from odyssey.api.telehealth.models import (
    TelehealthBookings,
    TelehealthMeetingRooms, 
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
)
from odyssey.api.telehealth.schemas import (
    TelehealthBookingsSchema,
    TelehealthBookingsOutputSchema,
    TelehealthMeetingRoomSchema,
    TelehealthQueueClientPoolSchema,
    TelehealthQueueClientPoolOutputSchema,
    TelehealthStaffAvailabilitySchema,
    TelehealthStaffAvailabilityOutputSchema,
    TelehealthTimeSelectOutputSchema
) 
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import TWILIO_ACCESS_KEY_TTL, DAY_OF_WEEK
from odyssey.utils.errors import GenericNotFound, InputError, UnauthorizedUser
from odyssey.utils.misc import check_client_existence, check_staff_existence, grab_twilio_credentials

ns = api.namespace('telehealth', description='telehealth bookings management API')

@ns.route('/client/time-select2/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID'})
class TelehealthClientTimeSelectApi2(Resource):                               
    
    @token_auth.login_required
    @responds(schema=TelehealthTimeSelectOutputSchema,api=ns, status_code=201)
    def get(self,user_id):
        """
        Returns the list of notifications for the given user_id
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
        duration = client_in_queue.duration
        # convert client's target date to day_of_week
        target_date = client_in_queue.target_date.date()
        
        # 0 is Monday, 6 is Sunday
        weekday_id = target_date.weekday()
        weekday_str = DAY_OF_WEEK[weekday_id]
        
        # This should return ALL staff available on that given day.
        # TODO, MUST INCLUDE PROFESSION TYPE FILTER, perhaps delete down low
        staff_availability = db.session.query(TelehealthStaffAvailability, StaffRoles)\
            .join(StaffRoles, StaffRoles.user_id==TelehealthStaffAvailability.user_id)\
                .filter(TelehealthStaffAvailability.day_of_week==weekday_str, StaffRoles.role==client_in_queue.profession_type).all()
        #### TESTING NOTES:
        ####   test1 - test with weekday_str when we have 0 availabilities (check if staff_availability is empty)
        
        # TODO if no staff availability do something
        breakpoint()
        if not staff_availability:
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
        for availability, _ in staff_availability:
            staff_user_id = availability.user_id
            if staff_user_id not in available:
                available[staff_user_id] = []
                staff_user_id_arr.append(staff_user_id)
            available[staff_user_id].append(availability.booking_window_id)

        # TODO simulate client staff bookings, delete this
        # TODO Must call client and staff bookings individually 

        # Now, grab all of the bookings for that client and all staff on the given target date
        # This is necessary to subtract from the staff_availability above.
        bookings = TelehealthBookings.query.filter_by(target_date=target_date).all()
        # Now, subtract booking times from staff availability and generate the actual times a staff member is free
        removedNum = {}
        for booking in bookings:
            staff_id = booking.staff_user_id
            if staff_id in available:
                if staff_id not in removedNum:
                    removedNum[staff_id] = []                
                for num in range(booking.booking_window_id_start_time,booking.booking_window_id_end_time+1):
                    if num in available[staff_id]:
                        available[staff_id].remove(num)
                        removedNum[staff_id].append(num)
            else:
                # This staff_user_id should not have availability on this day
                continue
        # convert time IDs to actual times for clients to select
        time_inc = LookupBookingTimeIncrements.query.all()
        # NOTE: It might be a good idea to shuffle user_id_arr and only select up to 10 (?) staff members 
        # to reduce the time complexity
        # user_id_arr = [1,2,3,4,5]
        # user_id_arr.random() -> [3,5,2,1,4]
        # user_id_arr[0:3]
        timeArr = {}
        test = []
        for staff_id in staff_user_id_arr:
            if staff_id not in removedNum:
                removedNum[staff_id] = []             
            for idx,time_id in enumerate(available[staff_id]):
                if idx + 1 < len(available[staff_id]):
                    if available[staff_id][idx+1] - time_id < idx_delta and time_id + idx_delta < available[staff_id][-1]:
                        if time_inc[time_id].start_time.minute%15 == 0:
                            if time_inc[time_id] not in timeArr:
                                timeArr[time_inc[time_id]] = []
                            if time_id+idx_delta in removedNum[staff_id]:
                                continue
                            else:
                                timeArr[time_inc[time_id]].append(staff_id)
                                test.append({ 'time_id': time_id,
                                            'staff_user_id': staff_id,
                                            'start_time': time_inc[time_id].start_time,
                                            'end_time':time_inc[time_id+idx_delta].end_time})
                    
                    else:
                        continue
                else:
                    continue

        times = []

        for time in timeArr:
            if len(timeArr[time]) > 1:
                random.shuffle(timeArr[time])
                times.append({'staff_user_id': timeArr[time][0],
                            'start_time': time.start_time, 
                            'end_time': time_inc[time.idx+idx_delta].end_time})
            else:
                times.append({'staff_user_id': timeArr[time][0],
                            'start_time': time.start_time, 
                            'end_time': time_inc[time.idx+idx_delta].end_time})                

        times.sort(key=sortStartTime)

        payload = {'appointment_times': times,
                   'total_options': len(times)}

        return payload


@ns.route('/client/time-select/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID'})
class TelehealthClientTimeSelectApi(Resource):                               
    
    @token_auth.login_required
    @responds(schema=TelehealthTimeSelectOutputSchema,api=ns, status_code=201)
    def get(self,user_id):
        """
        Returns the list of notifications for the given user_id
        """
        # Check if the client exists
        
        check_client_existence(user_id)

        # grab the client at the top of the queue?
        # Need to grab this for to grab the closest target_date / priority date
        # --------------------------------------------------------------------------
        # TODO: client_in_queue, is a list where we are supposed to grab from the top.
        # What if that client does not select a time, how do we move to the next person in the queue
        # client_in_queue MUST be the user_id
        # 
        # --------------------------------------------------------------------------
        client_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id).order_by(TelehealthQueueClientPool.priority.desc(),TelehealthQueueClientPool.target_date.asc()).first()
        duration = client_in_queue.duration
        # convert client's target date to day_of_week
        target_date = client_in_queue.target_date.date()
        
        # 0 is Monday, 6 is Sunday
        weekday_id = target_date.weekday()
        weekday_str = DAY_OF_WEEK[weekday_id]
        
        # This should return ALL staff available on that given day.
        # TODO, MUST INCLUDE PROFESSION TYPE FILTER, perhaps delete down low
        staff_availability = TelehealthStaffAvailability.query.filter_by(day_of_week=weekday_str).order_by(TelehealthStaffAvailability.user_id.asc()).all() 

        # Duration is taken from the client queue.
        # we divide it by 5 because our look up tables are in increments of 5 mintues
        # so, this represents the number of time blocks we will need to look at.
        # The subtract 1 is due to the indices having start_time and end_times, so 100 - 103 is 100.start_time to 103.end_time which is
        # the 20 minute duration
        idx_delta = int(duration/5) - 1
 
        # TODO will need to incorporate timezone information
        available = {}
        # TODO user_id_arr is staff_user_id_arr
        user_id_arr = []
        # Loop through all staff that have indicated they are available on that day of the week
        #
        # The expected output is the first and last index of their time blocks, AKA:
        # availability[staff_user_id] = [[100, 120], [145, 160]]
        #
        for availability in staff_availability:
            staff_user_id = availability.user_id
            # if userSwitch == 0:
            #     refUser = availabilty.user_id
            #     userSwitch = 1
            # if staff_user_id != refUser:

            if staff_user_id not in user_id_arr:
                booking_id_arr = []
                user_id_arr.append(staff_user_id)
                available[staff_user_id] = []
                idx1 = availability.booking_window_id+1
                booking_id_arr.append(idx1)
            else:
                idx2 = availability.booking_window_id+1          
                if idx2 - idx1 > 1:
                    # time gap detected
                    booking_id_arr.append(idx1)
                    available[staff_user_id].append(booking_id_arr)
                    booking_id_arr = []
                    booking_id_arr.append(idx2)
                idx1 = idx2
        booking_id_arr.append(idx2)
        available[staff_user_id].append(booking_id_arr)
        # breakpoint()
        # TODO simulate client staff bookings, delete this
        # TODO Must call client and staff bookings individually 

        # Now, grab all of the bookings for that client and all staff on the given target date
        # This is necessary to subtract from the staff_availability above.
        bookings = TelehealthBookings.query.filter_by(client_user_id=user_id,target_date=target_date).all()
        # Now, subtract booking times from staff availability and generate the actual times a staff member is free
        actual_open_time = {}
        for booking in bookings:
            staff_id = booking.staff_user_id
            if staff_id in available:
                if staff_id not in actual_open_time:
                    actual_open_time[staff_id] = []
                idx = 0
                # This while loop with a dynamic available is needed because as we subtract times from 
                # Staff availability, we need to split up the new time available windows.
                while idx < len(available[staff_id]):
                    # if the available time window is already less than session duration, skip this block of time
                    popped = False
                    avail = available[staff_id][idx]
                    if avail[1] - avail[0] < idx_delta:
                        continue
                    if booking.booking_window_id_start_time > avail[0] and\
                        booking.booking_window_id_end_time < avail[1]:
                        
                        block_end = booking.booking_window_id_start_time - 1
                        block_start = booking.booking_window_id_end_time + 1
                        # if the available time window is already less than session duration, skip this block of time
                        if block_end - avail[0] >= idx_delta:
                            if not popped:
                                available[staff_id].pop(idx)
                                popped = True 
                            available[staff_id].append([avail[0],block_end])
                            actual_open_time[staff_id].append([avail[0],block_end])
                        if avail[1] - block_start >= idx_delta:
                            if not popped:
                                available[staff_id].pop(idx)
                                popped = True
                            available[staff_id].append([block_start,avail[1]])                            
                            actual_open_time[staff_id].append([block_start,avail[1]])

                    idx+=1
            else:
                # This staff_user_id should not have availability on this day
                continue
        # convert time IDs to actual times for clients to select
        time_inc = LookupBookingTimeIncrements.query.all()
        times = []

        # NOTE: It might be a good idea to shuffle user_id_arr and only select up to 10 (?) staff members 
        # to reduce the time complexity
        # user_id_arr = [1,2,3,4,5]
        # user_id_arr.random() -> [3,5,2,1,4]
        # user_id_arr[0:3]
        for staff_id in user_id_arr:
            # times[staff_id] = []
            for time_ids in available[staff_id]:
                idx = time_ids[0]
                # This moving index is used to offer times in 5 minute increments.
                # For a 20 minute session, you can technically offer:
                # 1:00 - 1:20, 1:05 - 1:25, 1:10 - 1:30 etc
                while idx + idx_delta < time_ids[1]:
                    if time_inc[idx].start_time.minute%15 == 0:
                        times.append({'staff_user_id': staff_id,
                                    'start_time': time_inc[idx].start_time, 
                                    'end_time': time_inc[idx+idx_delta].end_time})
                    idx+=1
        
        # sort the queue based on target date and priority
        payload = {'appointment_times': times,
                   'total_options': len(times)}
        # breakpoint()
        return payload

@ns.route('/bookings/')
@ns.doc(params={'client_user_id': 'Client User ID',
                'staff_user_id' : 'Staff User ID'}) 
class TelehealthBookingsApi(Resource):
    """
    This API resource is used to get, post, and delete the user's in the queue.
    """        
    @responds(schema=TelehealthBookingsOutputSchema, api=ns, status_code=201)
    def get(self):
        """
        Returns the list of bookings for clients and/or staff
        """

        client_user_id = request.args.get('client_user_id', type=int)

        staff_user_id = request.args.get('staff_user_id', type=int)

        if not client_user_id and not staff_user_id:
            raise InputError(status_code=405,message='Must include at least one staff or client ID.')

        if client_user_id and staff_user_id:
            # Check client existence
            check_client_existence(client_user_id)  
            check_staff_existence(staff_user_id)      
            # grab the whole queue
            booking = TelehealthBookings.query.filter_by(client_user_id=client_user_id,staff_user_id=staff_user_id).order_by(TelehealthBookings.target_date.asc()).all()
        elif client_user_id and not staff_user_id:
            # Check client existence
            check_client_existence(client_user_id)        
            # grab the whole queue
            booking = TelehealthBookings.query.filter_by(client_user_id=client_user_id).order_by(TelehealthBookings.target_date.asc()).all()
        elif staff_user_id and not client_user_id:
            # Check staff existence
            check_staff_existence(staff_user_id)        
            # grab the whole queue
            booking = TelehealthBookings.query.filter_by(staff_user_id=staff_user_id).order_by(TelehealthBookings.target_date.asc()).all()
        
        
        # sort the queue based on target date and priority
        payload = {'bookings': booking,
                   'all_bookings': len(booking)}

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

        request.parsed_obj.client_user_id = client_user_id
        request.parsed_obj.staff_user_id = staff_user_id
        db.session.add(request.parsed_obj)
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

        meeting_room = TelehealthMeetingRooms(staff_user_id=staff_user.user_id, client_user_id=user_id)
        meeting_room.generate_meeting_room_name()
        
        ##
        # Query the Twilio APi to provision a new meeting room
        ##
        twilio_credentials = grab_twilio_credentials()

        # TODO: configure meeting room
        # meeting type (group by default), participant limit , callbacks

        # API access for the staff user to specifically access this chat room
        token = AccessToken(twilio_credentials['account_sid'], twilio_credentials['api_key'], twilio_credentials['api_key_secret'],
                         identity=staff_user.modobio_id, ttl=TWILIO_ACCESS_KEY_TTL)
        token.add_grant(VideoGrant(room=meeting_room.room_name))
        meeting_room.staff_access_token = token.to_jwt()
        meeting_room.__dict__['access_token'] = meeting_room.staff_access_token
        db.session.add(meeting_room)
        db.session.commit() 
        return meeting_room

@ns.route('/meeting-room/access-token/<int:room_id>/')
@ns.doc(params={'room_id': 'room ID number'})
class ProvisionMeetingRooms(Resource):
    """
    For generating and retrieving meeting room access tokens
    """
    @token_auth.login_required
    @responds(schema = TelehealthMeetingRoomSchema, status_code=201, api=ns)
    def post(self, room_id):
        """
        Generate a new Twilio access token with a grant for the meeting room id provided

        Users may only be granted access if they are one of the two participants.
        """
        client_user, _ = token_auth.current_user()

        meeting_room = TelehealthMeetingRooms.query.filter_by(client_user_id=client_user.user_id, room_id=room_id).one_or_none()
        if not meeting_room:
            raise GenericNotFound(message="no meeting room found")
        elif meeting_room.client_user_id != client_user.user_id:
            raise UnauthorizedUser(message='user not part of chat room')

        twilio_credentials = grab_twilio_credentials()

        # API access for the staff user to specifically access this chat room
        token = AccessToken(twilio_credentials['account_sid'], twilio_credentials['api_key'], twilio_credentials['api_key_secret'],
                         identity=client_user.modobio_id, ttl=TWILIO_ACCESS_KEY_TTL)
        token.add_grant(VideoGrant(room=meeting_room.room_name))
        meeting_room.client_access_token = token.to_jwt()
        meeting_room.__dict__['access_token'] = meeting_room.client_access_token
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
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    # This is the 2+ iteration through this block
                    # now, idx2 should be greater than idx1 because idx1 was stored in the 
                    # previous iteration
                    idx2 = time.booking_window_id
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
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                tueArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Wednesday':
                if len(wedArrIdx) == 0:
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                wedArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Thursday':
                if len(thuArrIdx) == 0:
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                thuArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Friday':
                if len(friArrIdx) == 0:
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                friArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Saturday':
                if len(satArrIdx) == 0:
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
                    idx1 = idx2
                satArrIdx.append(time.booking_window_id)
            elif time.day_of_week == 'Sunday':
                if len(sunArrIdx) == 0:
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id
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
                        startIdx = inc.idx - 1
                    elif(time['end_time'] == inc.end_time):
                        endIdx = inc.idx - 1
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
        appointment_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id,target_date=request.parsed_obj.target_date).one_or_none()

        if not appointment_in_queue:
            request.parsed_obj.user_id = user_id
            db.session.add(request.parsed_obj)
            db.session.commit()
        else:
            raise InputError(status_code=405,message='User {} already has an appointment for this date.'.format(user_id))

        return 200

    @token_auth.login_required()
    @accepts(schema=TelehealthQueueClientPoolSchema, api=ns)
    def delete(self, user_id):
        #Search for user by user_id in User table
        check_client_existence(user_id)
        appointment_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id,target_date=request.parsed_obj.target_date).one_or_none()
        if appointment_in_queue:
            db.session.delete(appointment_in_queue)
            db.session.commit()
        else:
            raise InputError(status_code=405,message='User {} does not have that date to delete'.format(user_id))

        return 200

def sortStartTime(val):
    return val['start_time']