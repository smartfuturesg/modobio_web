
from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

from odyssey import db
from odyssey.api import api
from odyssey.api.telehealth.models import TelehealthMeetingRooms, TelehealthQueueClientPool
from odyssey.api.telehealth.schemas import (
    TelehealthMeetingRoomSchema,
    TelehealthQueueClientPoolSchema,
    TelehealthQueueClientPoolOutputSchema
) 
from odyssey.utils.auth import token_auth
from odyssey.utils.constants import TWILIO_ACCESS_KEY_TTL
from odyssey.utils.errors import GenericNotFound, InputError, UnauthorizedUser
from odyssey.utils.misc import check_client_existence, grab_twilio_credentials

ns = api.namespace('telehealth', description='telehealth bookings management API')

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

        return

    @token_auth.login_required
    @responds(schema = TelehealthMeetingRoomSchema, status_code=200, api=ns)
    def get(self, room_id):
        """
        Check the meeting status

        should just return vital details on meeting rooms
        """
        meeting_room = TelehealthMeetingRooms.query.filter_by(room_id=room_id).one_or_none()
        return meeting_room

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
