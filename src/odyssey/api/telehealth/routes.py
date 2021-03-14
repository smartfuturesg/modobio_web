
from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
import datetime as dt

from odyssey import db
from odyssey.api import api

from odyssey.api.lookup.models import (
    LookupBookingTimeIncrements
)

from odyssey.api.telehealth.models import (
    TelehealthMeetingRooms, 
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
)
from odyssey.api.telehealth.schemas import (
    TelehealthMeetingRoomSchema,
    TelehealthQueueClientPoolSchema,
    TelehealthQueueClientPoolOutputSchema,
    TelehealthStaffAvailabilitySchema,
    TelehealthStaffAvailabilityOutputSchema
) 
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import TWILIO_ACCESS_KEY_TTL, DAY_OF_WEEK
from odyssey.utils.errors import GenericNotFound, InputError, UnauthorizedUser
from odyssey.utils.misc import check_client_existence, check_staff_existence, grab_twilio_credentials

import numpy as np

ns = api.namespace('telehealth', description='telehealth bookings management API')

@ns.route('/client/time-select/')
@ns.doc(params={'user_id': 'User ID number'})
class TelehealthTimeSelectApi(Resource):
    @token_auth.login_required
    @responds(status_code=201,api=ns)
    def get(self):

        # First, grab the queue, and grab the person at the top
        queue = TelehealthQueueClientPool.query.order_by(TelehealthQueueClientPool.priority.desc(),TelehealthQueueClientPool.target_date.asc()).first()
        
        # convert that day from the queue to a day of the week
        
        # datetime.weekday() returns:
        # Monday 0, 6 is Sunday
        day_of_week_idx = queue.target_date.weekday()
        day_of_week = DAY_OF_WEEK[day_of_week_idx]

        staff_availability = TelehealthStaffAvailability.query.filter_by(day_of_week=day_of_week).all()

        # breakpoint()

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
        """
        # grab staff availability
        check_staff_existence(user_id)
        availability = TelehealthStaffAvailability.query.filter_by(user_id=user_id).\
                        order_by(TelehealthStaffAvailability.day_of_week.asc(),TelehealthStaffAvailability.booking_window_id.asc()).all()
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
        for idx,time in enumerate(availability):
            
            currDay = time.day_of_week

            if daySwitch == 0:
                refDay = time.day_of_week 
                daySwitch = 1

            if currDay != refDay:
                end_time = booking_increments[idx2].end_time
                orderedArr[refDay].append({'day_of_week':refDay,'start_time': start_time, 'end_time': end_time})
                daySwitch = 0

            if time.day_of_week == 'Monday':                
                if len(monArrIdx) == 0:
                    idx1 = time.booking_window_id
                    start_time = booking_increments[idx1].start_time
                else:
                    idx2 = time.booking_window_id             
                    if idx2 - idx1 > 1:
                        end_time = booking_increments[idx1].end_time
                        orderedArr[time.day_of_week].append({'day_of_week':time.day_of_week, 'start_time': start_time, 'end_time': end_time})
                        start_time = booking_increments[idx2].start_time
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

        end_time = booking_increments[idx2].end_time
        orderedArr[refDay].append({'day_of_week':refDay,'start_time': start_time, 'end_time': end_time})            

        monArr = orderedArr['Monday']
        tueArr = orderedArr['Tuesday']
        wedArr = orderedArr['Wednesday']
        thuArr = orderedArr['Thursday']
        friArr = orderedArr['Friday']
        satArr = orderedArr['Saturday']
        sunArr = orderedArr['Sunday']
        
        orderedArray = []
        orderedArray = [*monArr, *tueArr, *wedArr, *thuArr, *friArr, *satArr, *sunArr]

        payload = {}
        payload['availability'] = orderedArray
        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthStaffAvailabilityOutputSchema, api=ns)
    @responds(schema=TelehealthStaffAvailabilityOutputSchema, api=ns, status_code=201)
    def post(self,user_id):
        """
        Returns the staff availability

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

        payload = {}        
        payload['availability'] = []
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
                        payload['availability'].append(time)
                    else:
                        continue

        db.session.commit()
        return payload

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
