from bson import ObjectId
from datetime import datetime, time, timedelta
from dateutil import tz
from itertools import groupby
from operator import itemgetter
import logging
logger = logging.getLogger(__name__)

import secrets

from datetime import datetime, time, timedelta
from dateutil import tz

from flask import request, current_app, g, url_for
from flask_accepts import accepts, responds
from flask_restx import Resource, Namespace
from sqlalchemy import select, or_
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant, ChatGrant
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import db, mongo
from odyssey.api.lookup.models import (
    LookupBookingTimeIncrements
)
from odyssey.api.lookup.models import LookupTerritoriesOfOperations
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.staff.models import StaffRoles
from odyssey.api.telehealth.models import (
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
    TelehealthStaffAvailabilityConflictSchema,
    TelehealthBookingDetailsSchema,
    TelehealthBookingDetailsGetSchema,
    TelehealthBookingsPUTSchema,
    TelehealthTranscriptsSchema,
)
from odyssey.api.user.models import User
from odyssey.api.lookup.models import (
    LookupTerritoriesOfOperations
)
from odyssey.api.payment.models import PaymentMethods
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.integrations.instamed import cancel_telehealth_appointment
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
    check_client_existence, 
    check_staff_existence
)
from odyssey.integrations.twilio import Twilio
import odyssey.utils.telehealth as telehealth_utils
from odyssey.utils.file_handling import FileHandling
from odyssey.utils.base.resources import BaseResource
from odyssey.tasks.tasks import cleanup_unended_call, store_telehealth_transcript

ns = Namespace('telehealth', description='telehealth bookings management API')

@ns.route('/bookings/meeting-room/access-token/<int:booking_id>/')
class TelehealthBookingsRoomAccessTokenApi(BaseResource):
    """
    This endpoint is used to GET the staff and client's TWILIO access tokens so they can
    access their chats and videos.

    Here, we create the Booking Meeting Room.

    Call start
    """
    @token_auth.login_required
    @responds(schema=TelehealthBookingMeetingRoomsTokensSchema, api=ns, status_code=200)
    def get(self, booking_id):
        current_user, _ = token_auth.current_user()

        booking = TelehealthBookings.query.get(booking_id)

        # below are some checks to ensure the call may begin:
        # - requester must be one of the participants
        # - the call must be started by the practitioner
        # - calls cannot begin more than 10 minuted before scheduled time 
        # - calls may not begin AFTER the scheduled appointment time
        if not booking:
            raise BadRequest('no booking found')

        # make sure the requester is one of the participants
        if not (current_user.user_id == booking.client_user_id or
                current_user.user_id == booking.staff_user_id):
            raise Unauthorized('You must be a participant in this booking.')

        # check call timing
        booking_start_time = datetime.combine(
            date=booking.target_date_utc,
            time = LookupBookingTimeIncrements.query.filter_by(idx = booking.booking_window_id_start_time_utc).one_or_none().start_time)
        current_time_utc = datetime.utcnow()
        call_start_offset = (booking_start_time - current_time_utc).total_seconds()

        #calculate booking duration
        increment_data = telehealth_utils.get_booking_increment_data()
        if booking.booking_window_id_end_time < booking.booking_window_id_start_time:
            #booking crosses midnight
            highest_index = increment_data['max_idx'] + 1
            duration = (highest_index - booking.booking_window_id_start_time + \
                booking.booking_window_id_end_time) * increment_data['length']
        else:
            duration = (booking.booking_window_id_end_time - booking.booking_window_id_start_time + 1) \
                * increment_data['length']
        
        if call_start_offset > 600 or call_start_offset < -60*duration:
            raise BadRequest('Request to start call occured too soon or after the scheduled call has ended')
        
        # Create telehealth meeting room entry
        # each telehealth session is given a unique meeting room
        twilio_obj = Twilio()
        meeting_room = db.session.execute(
            select(TelehealthMeetingRooms).
            where(
                TelehealthMeetingRooms.booking_id == booking_id,
                )).scalar()

        # if there is no meeting room, the call has not yet begun. 
        # only practitioners may initiate a call
        if not meeting_room:
            if current_user.user_id == booking.staff_user_id:
                meeting_room = TelehealthMeetingRooms(
                    booking_id=booking_id,
                    staff_user_id=booking.staff_user_id,
                    client_user_id=booking.client_user_id)
                meeting_room.room_name = twilio_obj.generate_meeting_room_name()
            else:
                raise BadRequest('Telehealth call may only be initiated by practitioner')

        # Create access token for users to access the Twilio API
        # Add grant for video room access using meeting room name just created
        # Twilio will automatically create a new room by this name.
        # TODO: configure meeting room
        # meeting type (group by default), participant limit , callbacks
        
        token, video_room_sid = twilio_obj.create_twilio_access_token(current_user.modobio_id, meeting_room_name=meeting_room.room_name)
        meeting_room.sid = video_room_sid

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

        # Update TelehealthBookingStatus to 'In Progress'
        booking.status = 'In Progress'
        db.session.commit()

        # schedule celery task to ensure call is completed 10 min after utc end date_time
        booking_start_time = LookupBookingTimeIncrements.query.get(booking.booking_window_id_start_time_utc).start_time
        
        cleanup_eta = datetime.combine(booking.target_date_utc, booking_start_time, tz.UTC) + timedelta(minutes=duration) + timedelta(minutes=10)
        
        if not current_app.config['TESTING']:
            cleanup_unended_call.apply_async((booking.idx,), eta=cleanup_eta)
        
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
class TelehealthClientTimeSelectApi(BaseResource):

    @token_auth.login_required
    @responds(schema=TelehealthTimeSelectOutputSchema,api=ns, status_code=200)
    def get(self, user_id):
        """
        Checks the booking requirements stored in the client queue

        Responds with available booking times localized to the client's timezone
        """
        check_client_existence(user_id)

        client_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id).order_by(TelehealthQueueClientPool.priority.desc(),TelehealthQueueClientPool.target_date.asc()).first()
        if not client_in_queue:
            raise BadRequest('Client is not in the queue.')

        time_inc = LookupBookingTimeIncrements.query.all()

        local_target_date = client_in_queue.target_date
        client_tz = client_in_queue.timezone
        duration = client_in_queue.duration
        profession_type = client_in_queue.profession_type

        days_out = 0
        # days_available = 
        # {local_target_date(datetime.date):
        #   {start_time_idx_1: 
        #       {'date_start_utc': datetime.date,
        #         'practitioner_ids': {user_id, user_id (set)}
        #       }
        #   },
        #   {start_time_idx_2: 
        #       {'date_start_utc': datetime.date,
        #         'practitioner_ids':  {user_id, user_id (set)}
        #       }
        #   }
        #}
        days_available = {}
        times_available = 0
        while days_out <= 14 and times_available < 10:
            local_target_date2 = local_target_date + timedelta(days=days_out)
            day_start_utc, start_time_window_utc, day_end_utc, end_time_window_utc = \
                telehealth_utils.get_utc_start_day_time(local_target_date2, client_tz)
            
            time_blocks = telehealth_utils.get_possible_ranges(
                day_start_utc,
                day_start_utc.weekday(), 
                start_time_window_utc.idx, 
                day_end_utc.weekday(), 
                end_time_window_utc.idx,
                duration)

            # available_times_with_practitioners =
            # {start_time_idx: {'date_start_utc': datetime.date, 'practitioner_ids': {set of available user_ids}}
            # sample -> {1: {'date_start_utc': datetime.date(2021, 10, 27), 'practitioner_ids': {10}}
            available_times_with_practitioners = {}
            practitioner_ids_set = set() # {user_id, user_id} set of user_id of available practitioners
            for block in time_blocks:
                _practitioner_ids = telehealth_utils.get_practitioners_available(time_blocks[block], client_in_queue)
                
                #if the user has a staff + client account, it may be possible for their staff account
                #to appear as an option when attempting to book a meeting as a client
                #to prevent this, we check if the logged in user's id is in the list of practitioners and remove it
                if token_auth.current_user()[0].user_id in _practitioner_ids:
                    _practitioner_ids.remove(token_auth.current_user()[0].user_id)
                    
                if _practitioner_ids:
                    date1, day1, day1_start, day1_end = time_blocks[block][0]
                    available_times_with_practitioners[block] = {
                        'date_start_utc': date1.date(),
                        'practitioner_ids': _practitioner_ids}
                    practitioner_ids_set.update(_practitioner_ids)

            if available_times_with_practitioners:
                days_available[local_target_date2.date()] = available_times_with_practitioners

            times_available += len(available_times_with_practitioners)
            days_out += 1
        
        if not days_available:
            raise BadRequest('No staff available for the upcoming two weeks.')

        # get practitioners details only once
        # dict {user_id: {firstname, lastname, consult_cost, gender, bio, profile_pictures, hourly_consult_rate}}
        practitioners_info = telehealth_utils.get_practitioner_details(practitioner_ids_set, profession_type, duration)

        ##
        #  Wheel availability request
        ##
        # wheel = Wheel() 
        #########################

      
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

        #times.sort(key=lambda t: t['start_time'])    
        #times.sort(key=lambda t: t['target_date'])

        #payload = {'appointment_times': times,
        #           'total_options': len(times)}

        #buffer not taken into consideration here becuase that only matters to practitioner not client
        final_dict = []
        for day in days_available:
            for time in days_available[day]:
                target_date_utc = days_available[day][time]['date_start_utc']                
                client_window_id_start_time_utc = time
                start_time_utc = time_inc[client_window_id_start_time_utc - 1].start_time

                # client localize target_date_utc + utc_start_time + timezone
                datetime_start = datetime.combine(target_date_utc, start_time_utc, tz.UTC).astimezone(tz.gettz(client_tz))
                datetime_end = datetime_start + timedelta(minutes=duration)
                localized_window_start = LookupBookingTimeIncrements.query.filter_by(start_time=datetime_start.time()).first().idx
                localized_window_end = LookupBookingTimeIncrements.query.filter_by(end_time=datetime_end.time()).first().idx
                
                final_dict.append({
                    'practitioners_available_ids': list(days_available[day][time]['practitioner_ids']),
                    'target_date': datetime_start.date(),
                    'start_time': datetime_start.time(),
                    'end_time': datetime_end.time(),
                    'booking_window_id_start_time': localized_window_start,
                    'booking_window_id_end_time': localized_window_end
                })
        payload = {'appointment_times': final_dict,
                   'total_options': len(final_dict),
                   'practitioners_info': practitioners_info}

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
                'booking_id': 'booking_id',
                'page': 'pagination index',
                'per_page': 'results per page'})
    def get(self):
        """
        Returns the list of bookings for clients and/or staff
        """
        current_user, _ = token_auth.current_user()

        client_user_id = request.args.get('client_user_id', type=int)
        staff_user_id = request.args.get('staff_user_id', type=int)
        booking_id = request.args.get('booking_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

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
            raise BadRequest('Must include at least "client_user_id", "staff_user_id", '
                             'or "booking_id".')
        elif booking_id:
            # 1. booking_id provided, any other parameter is ignored, only returns booking to participants or cs
            query_filter = {'idx': booking_id}

        elif staff_user_id and not client_user_id:
            # 3. only staff_user_id provided, return all bookings for such user_id if logged-in user is same user or client services
            if not (current_user.user_id == staff_user_id or
                    'client_services' in [role.role for role in current_user.roles]):
                raise Unauthorized('You must be a participant in this booking.')
            query_filter = {'staff_user_id': staff_user_id}
        
        elif client_user_id and not staff_user_id:
            #4. only client_user_id provided, return all bookings for such user_id if loggedin user is same user or cs
            if not (current_user.user_id == client_user_id or
                    'client_services' in [role.role for role in current_user.roles]):
                raise Unauthorized('You must be a participant in this booking.')
            query_filter = {'client_user_id': client_user_id}
       
        else:
            #5. both client and user id's are provided, return bookings where both exist if loggedin is either or cs
            if not (current_user.user_id == client_user_id or
                    current_user.user_id == staff_user_id or
                    'client_services' in [role.role for role in current_user.roles]):
                raise Unauthorized('You must be a participant in this booking.')
            query_filter = {'staff_user_id': staff_user_id, 'client_user_id': client_user_id}
            
        # grab the bookings using the filter generated above
        bookings_query = TelehealthBookings.query.filter_by(**query_filter).\
            order_by(TelehealthBookings.target_date_utc.desc(), TelehealthBookings.booking_window_id_start_time_utc.desc()).paginate(page,per_page,error_out=False)
        bookings = bookings_query.items

        # ensure requested booking_id is allowed
        if booking_id and len(bookings) == 1:
            if not (current_user.user_id == bookings[0].client_user_id or
                    current_user.user_id == bookings[0].staff_user_id or
                    'client_services' in [role.role for role in current_user.roles]):
                raise Unauthorized('You must be a participant in this booking.')
        
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
            
            #calculate booking duration in minutes
            increment_data = telehealth_utils.get_booking_increment_data()
            if booking.booking_window_id_end_time_utc < booking.booking_window_id_start_time_utc:
                #booking crosses midnight
                highest_index = increment_data['max_idx'] + 1
                duration = (highest_index - booking.booking_window_id_start_time + \
                    booking.booking_window_id_end_time) * increment_data['length']
            else:
                duration = (booking.booking_window_id_end_time - booking.booking_window_id_start_time + 1) \
                    * increment_data['length']

            end_time_utc = start_time_utc + timedelta(minutes=duration)

            practitioner['start_date_localized'] = start_time_utc.astimezone(tz.gettz(booking.staff_timezone)).date()
            practitioner['start_time_localized'] = start_time_utc.astimezone(tz.gettz(booking.staff_timezone)).time()
            practitioner['end_time_localized'] = end_time_utc.astimezone(tz.gettz(booking.staff_timezone)).time()

            client['timezone'] = booking.client_timezone
            client['start_date_localized'] = start_time_utc.astimezone(tz.gettz(booking.client_timezone)).date()
            client['start_time_localized'] = start_time_utc.astimezone(tz.gettz(booking.client_timezone)).time()
            client['end_time_localized'] = end_time_utc.astimezone(tz.gettz(booking.client_timezone)).time()
            # return the client profile_picture wdith=128 if the logged in user is the practitioner involved
            if current_user.user_id == booking.staff_user_id:
                image_paths = {pic.width: pic.image_path for pic in booking.client.client_info.profile_pictures}
                client['profile_picture'] = (fh.get_presigned_url(image_paths[128]) if image_paths else None)
            
            # if the associated chat room has an id for the mongo db entry of the transcript, generate a link to retrieve the 
            # transcript messages
            if booking.chat_room.transcript_object_id:
                transcript_url = request.url_root[:-1] + url_for('api.telehealth_telehealth_transcripts', booking_id = booking.idx)
                booking_chat_details = booking.chat_room.__dict__
                booking_chat_details['transcript_url'] = transcript_url
            else: 
                booking_chat_details = booking.chat_room.__dict__

            # check if a booking description has been added to the meeting
            booking_details = None
            if booking.booking_details:
                booking_details = booking.booking_details.details

            bookings_payload.append({
                'booking_id': booking.idx,
                'target_date_utc': booking.target_date_utc,
                'start_time_utc': start_time_utc.time(),
                'status': booking.status,
                'profession_type': booking.profession_type,
                'chat_room': booking_chat_details,
                'client_location_id': booking.client_location_id,
                'payment_method_id': booking.payment_method_id,
                'status_history': booking.status_history,
                'client': client,
                'practitioner': practitioner,
                'consult_rate': booking.consult_rate,
                'charged': booking.charged,
                'description': booking_details 
            })

        # Sort bookings by time then sort by date
        bookings_payload.sort(key=lambda t: t['start_time_utc'])
        bookings_payload.sort(key=lambda t: t['target_date_utc'])
        
        twilio = Twilio()
        # create twilio access token with chat grant 
        token, _ = twilio.create_twilio_access_token(current_user.modobio_id)
        
        payload = {
            'all_bookings': len(bookings_payload),
            'bookings': bookings_payload,
            'twilio_token': token,
            '_links': {
                '_prev': url_for('api.telehealth_telehealth_bookings_api', page=bookings_query.prev_num, per_page = per_page) if bookings_query.has_prev else None,
                '_next': url_for('api.telehealth_telehealth_bookings_api', page=bookings_query.next_num, per_page = per_page) if bookings_query.has_next else None,
            }
        }
        return payload

    @token_auth.login_required(user_type=('client',))
    @accepts(schema=TelehealthBookingsSchema(only=['booking_window_id_end_time','booking_window_id_start_time','target_date']), api=ns)
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
        #if request.parsed_obj.booking_window_id_start_time >= request.parsed_obj.booking_window_id_end_time:
        #    raise BadRequest('Start time must be before end time.')
        # NOTE commented out this check, the input for booking_window_id_end_time will not be taken into cosideration, 
        # only booking_window_id_start_time and target_date
        # TODO depricate requiring booking_window_id_end_time as an input

        client_user_id = request.args.get('client_user_id', type=int)
        if not client_user_id:
            raise BadRequest('Missing client ID.')
        # Check client existence
        self.check_user(client_user_id, user_type='client')

        staff_user_id = request.args.get('staff_user_id', type=int)
        if not staff_user_id:
            raise BadRequest('Missing practitioner ID.')    
        # Check staff existence
        self.check_user(staff_user_id, user_type='staff')
        
        if client_user_id == staff_user_id:
            raise BadRequest('Staff user id cannot be the same as client user id.')
        
        # make sure the requester is one of the participants
        if not (current_user.user_id == client_user_id or
                current_user.user_id == staff_user_id):
            raise BadRequest('You must be a participant in this booking.')

        time_inc = LookupBookingTimeIncrements.query.all()
        start_time_idx_dict = {item.start_time.isoformat() : item.idx for item in time_inc} # {datetime.time: booking_availability_id}
        # bring up client queue details
        client_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=client_user_id).one_or_none()
        if not client_in_queue:
            raise BadRequest('Client not in queue.')
        
        # requested duration in minutes
        duration = client_in_queue.duration

        # Verify target date is client's local today or in the future 
        client_tz = client_in_queue.timezone
        start_idx = request.parsed_obj.booking_window_id_start_time
        if (start_idx - 1) % 3 > 0:
            # verify time idx-1 is mulitple of 3. Only allowed start times are: X:00, X:15, X:30, X:45
            raise BadRequest("Invalid start time")

        start_time = time_inc[start_idx-1].start_time
        # datetime start localized to client's timezone
        target_date = datetime.combine(request.parsed_obj.target_date, time(hour=start_time.hour, minute=start_time.minute, tzinfo=tz.gettz(client_tz)))
        client_local_datetime_now = datetime.now(tz.gettz(client_tz)).replace(second=0,microsecond=0) + timedelta(hours=TELEHEALTH_BOOKING_LEAD_TIME_HRS)
        if target_date < client_local_datetime_now:
            raise BadRequest("Invalid target date or time")
        
        # update parsed_obj with client localized end 
        # NOTE currently ignorign the incoming 'booking_window_id_end_time' input
        # TODO coordinate with FE to stop requiring 'booking_window_id_end_time'
        target_date_end_time = (target_date + timedelta(minutes = duration))
        request.parsed_obj.booking_window_id_end_time = start_time_idx_dict[target_date_end_time.strftime('%H:%M:%S')] - 1

        # Localize the requested booking date and time to UTC
        target_start_datetime_utc = target_date.astimezone(tz.UTC)
        target_end_datetime_utc = target_start_datetime_utc + timedelta(minutes=duration)
        target_start_time_idx_utc = start_time_idx_dict[target_start_datetime_utc.strftime('%H:%M:%S')]
        target_end_time_idx_utc = start_time_idx_dict[target_end_datetime_utc.strftime('%H:%M:%S')] - 1
       
        # call on verify_availability, will raise an error if practitioner doens't have availability requested
        telehealth_utils.verify_availability(client_user_id, staff_user_id, target_start_time_idx_utc, 
            target_end_time_idx_utc, target_start_datetime_utc, target_end_datetime_utc,client_in_queue.location_id)      

        # staff and client may proceed with scheduling the booking, 
        # create the booking object
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
        request.parsed_obj.client_location_id = client_in_queue.location_id
        request.parsed_obj.payment_method_id = client_in_queue.payment_method_id
        request.parsed_obj.profession_type = client_in_queue.profession_type
        request.parsed_obj.medical_gender_preference = client_in_queue.medical_gender

        # check the practitioner's auto accept setting.
        if staff_settings.auto_confirm:
            request.parsed_obj.status = 'Accepted'
        else:
            request.parsed_obj.status = 'Pending'
            # TODO: here, we need to send some sort of notification to the staff member letting
            # them know they have a booking request.

        # save target date and booking window ids in UTC
        request.parsed_obj.booking_window_id_start_time_utc = target_start_time_idx_utc
        request.parsed_obj.booking_window_id_end_time_utc = target_end_time_idx_utc
        request.parsed_obj.target_date_utc = target_start_datetime_utc.date()

        # consultation rate to booking
        consult_rate = StaffRoles.query.filter_by(user_id=staff_user_id,role=client_in_queue.profession_type).one_or_none().consult_rate

        # Calculate time for display:
        # consulte_rate is in hours
        # 30 minutes -> 0.5*consult_rate
        # 60 minutes -> 1*consulte_rate
        # 90 minutes -> 1.5*consulte_rate
        if not consult_rate:
            raise BadRequest('Practitioner has not set a consult rate')
        rate = telehealth_utils.calculate_consult_rate(consult_rate,duration)
        request.parsed_obj.consult_rate = str(rate)

        db.session.add(request.parsed_obj)
        db.session.flush()


        # if the staff memebr is a wheel clinician, make booking request to wheel API
        booking_url = None
        ######### WHEEL ##########
        #wheel = Wheel()
        #wheel_clinician_ids = wheel.clinician_ids(key='user_id')
        #if staff_user_id in wheel_clinician_ids:
        #    external_booking_id, booking_url = wheel.make_booking_request(staff_user_id, client_user_id, client_in_queue.location_id, request.parsed_obj.idx, target_start_datetime_utc)
        #    request.parsed_obj.external_booking_id = external_booking_id
        
        twilio_obj = Twilio()
        # create Twilio conversation and store details in TelehealthChatrooms table
        conversation_sid = twilio_obj.create_telehealth_chatroom(booking_id = request.parsed_obj.idx)

        # create access token with chat grant for newly provisioned room
        token, _ = twilio_obj.create_twilio_access_token(current_user.modobio_id)

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

        telehealth_utils.add_booking_to_calendar(request.parsed_obj, 
                            booking_start_staff_localized, 
                            booking_end_staff_localized)
        db.session.commit()

        # create response payload
        booking = TelehealthBookings.query.filter_by(idx=request.parsed_obj.idx).first()
        client = {**booking.client.__dict__}
        client['timezone'] = booking.client_timezone
        client['start_date_localized'] = target_date.date()
        client['start_time_localized'] = target_date.time()
        client['end_time_localized'] = (target_date + timedelta(minutes=duration)).time()
        practitioner = {**booking.practitioner.__dict__}
        practitioner['timezone'] = booking.staff_timezone
        practitioner['start_date_localized'] = booking_start_staff_localized.date()
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
                'booking_url': booking_url,
                'consult_rate': booking.consult_rate
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
            raise BadRequest('Booking not found.')

        # Verify loggedin user is part of booking
        if not (current_user.user_id == booking.client_user_id or
                current_user.user_id == booking.staff_user_id):
            raise Unauthorized('You must be a participant in this booking.')

        data = request.get_json()

        payment_id = data.get('payment_method_id')
        # If user wants to change the payment method for booking
        if payment_id:
            # Verify it's the client that's trying to change the payment method
            if not current_user.user_id == booking.client_user_id:
                raise Unauthorized('Only client can update payment method.')

            # Verify payment method idx is valid from PaymentMethods
            # and that the payment method chosen is registered under the client_user_id
            if not PaymentMethods.query.filter_by(user_id=booking.client_user_id, idx=payment_id).one_or_none():
                raise BadRequest('Invalid payment method.')

        new_status = data.get('status')
        if new_status:
            # Can't update status to 'In Progress' through this endpoint
            # only practitioner can change status from pending to accepted
            # both client and practitioner can change status to canceled and completed
            if new_status in ('In Progress', 'Completed'):
                raise BadRequest('This status can only be updated at the start or end of a call.')

            elif (new_status in ('Pending', 'Accepted') and
                  current_user.user_id != booking.staff_user_id):
                raise Unauthorized('Only practitioner can update this status.')

            if new_status != 'Canceled':
                booking.update(data)
                db.session.commit()
            
            else:
                #if staff initiated cancellation, refund should be true
                #if client initiated, refund should be false
                if current_user.user_id == booking.staff_user_id:
                    cancel_telehealth_appointment(booking, reason="Practitioner Cancellation", refund=True)
                else:
                    cancel_telehealth_appointment(booking, refund=False)                


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
            raise BadRequest('Start time must be before end time.')

        client_user_id = request.args.get('client_user_id', type=int)

        if not client_user_id:
            raise BadRequest('Missing client ID.')

        staff_user_id = request.args.get('staff_user_id', type=int)

        if not staff_user_id:
            raise BadRequest('Missing Staff ID.')

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
            raise BadRequest('Booking not found.')

        db.session.delete(bookings)
        db.session.commit()


@ns.route('/meeting-room/new/<int:user_id>/')
@ns.deprecated
@ns.doc(params={'user_id': 'User ID number'})
class ProvisionMeetingRooms(BaseResource):
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
        twilio= Twilio()
        meeting_room = TelehealthMeetingRooms(staff_user_id=staff_user.user_id, client_user_id=user_id)
        meeting_room.room_name = twilio.generate_meeting_room_name()
        

        # Bring up chat room session. Chat rooms are intended to be between a client and staff
        # member and persist through all telehealth interactions between the two.
        # only one chat room will exist between each client-staff pair
        # If this is the first telehealth interaction between
        # the client and staff member, a room will be provisioned.

        twilio_credentials = twilio.grab_twilio_credentials()

        # get_chatroom helper function will take care of creating or bringing forward
        # previously created chat room and add user as a participant using their modobio_id
        conversation = twilio.get_chatroom(staff_user_id = staff_user.user_id,
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
class GrantMeetingRoomAccess(BaseResource):
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
            raise BadRequest('Meeting room not found.')
        elif meeting_room.client_user_id != client_user.user_id:
            raise Unauthorized('Not a participant of this meeting.')

        twilio= Twilio()
        twilio_credentials = twilio.grab_twilio_credentials()

        # get_chatroom helper function will take care of creating or bringing forward
        # previously created chat room and add user as a participant using their modobio_id
        conversation = twilio.get_chatroom(staff_user_id = meeting_room.staff_user_id,
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
class MeetingRoomStatusAPI(BaseResource):
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
class TelehealthSettingsStaffAvailabilityApi(BaseResource):
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
        
        monday = TelehealthStaffAvailability.query.filter_by(user_id=user_id, day_of_week='Monday').\
            order_by(TelehealthStaffAvailability.booking_window_id.asc()).all()
        tuesday = TelehealthStaffAvailability.query.filter_by(user_id=user_id, day_of_week='Tuesday').\
            order_by(TelehealthStaffAvailability.booking_window_id.asc()).all()
        wednesday = TelehealthStaffAvailability.query.filter_by(user_id=user_id, day_of_week='Wednesday').\
            order_by(TelehealthStaffAvailability.booking_window_id.asc()).all()
        thursday = TelehealthStaffAvailability.query.filter_by(user_id=user_id, day_of_week='Thursday').\
            order_by(TelehealthStaffAvailability.booking_window_id.asc()).all()
        friday = TelehealthStaffAvailability.query.filter_by(user_id=user_id, day_of_week='Friday').\
            order_by(TelehealthStaffAvailability.booking_window_id.asc()).all()
        saturday = TelehealthStaffAvailability.query.filter_by(user_id=user_id, day_of_week='Saturday').\
            order_by(TelehealthStaffAvailability.booking_window_id.asc()).all()
        sunday = TelehealthStaffAvailability.query.filter_by(user_id=user_id, day_of_week='Sunday').\
            order_by(TelehealthStaffAvailability.booking_window_id.asc()).all()
        
        availability = []
        availability.append(monday) if monday else None
        availability.append(tuesday) if tuesday else None
        availability.append(wednesday) if wednesday else None
        availability.append(thursday) if thursday else None
        availability.append(friday) if friday else None
        availability.append(saturday) if saturday else None
        availability.append(sunday) if sunday else None
        
        if not availability:
            return
        # return tzone and auto-confirm from TelehealthStaffSettings table
        payload = {
            'settings': {'timezone': availability[0][0].settings.timezone, 'auto_confirm': availability[0][0].settings.auto_confirm},
            'availability': []
        }
        
        # pull the static booking window ids
        booking_increments = LookupBookingTimeIncrements.query.all()

        # start_time and end_time are returned in UTC, 
        # the timzone returned in payload is practitioner's preferred tz
        for avail_day in availability:
            # find consecutive availability blocks for this day
            window_ids = enumerate([avail.booking_window_id for avail in avail_day])
            for k, g in groupby(window_ids, lambda x: x[0] - x[1]):
                # create a new list of availability indeces per block
                avail_time_block = list(map(itemgetter(1), g))
                start = booking_increments[avail_time_block[0] - 1].start_time # first idex in available time block
                end = booking_increments[avail_time_block[-1] - 1].end_time # last idex in available time block
                day_o_week = avail_day[0].day_of_week
                payload['availability'].append({'day_of_week': day_o_week, 'start_time': start, 'end_time':end})

        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthStaffAvailabilityOutputSchema, api=ns)
    @responds(schema=TelehealthStaffAvailabilityConflictSchema, api=ns, status_code=201)
    def post(self,user_id):
        """
        Posts the staff availability
        Times provided are converted to UTC and stored as such in the db.

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

        ######### WHEEL #########
        # prevent wheel clinicians from submitting telehealth availability
        # wheel = Wheel()
        # wheel_clinician_ids = wheel.clinician_ids(key='user_id')
        # if user_id in wheel_clinician_ids and request.parsed_obj['availability']:
        #     raise BadRequest('You can only edit your telehealth settings, not availability.')

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

        if request.parsed_obj['availability']:
            booking_increments = LookupBookingTimeIncrements.query.all()
            avail = request.parsed_obj['availability']

            if not request.parsed_obj['settings']:
                raise BadRequest('Missing required field settings.')

            # Update tzone and auto-confirm in telehealth staff settings table once
            settings_data = request.parsed_obj['settings']
            settings_data.user_id = user_id
            db.session.add(settings_data)

            data = {'user_id': user_id}
            # Loop through the input payload of start_time and end_times
            for avail_time in avail:
                # end time must be after start time
                if avail_time['start_time'] > avail_time['end_time']:
                    db.session.rollback()
                    raise BadRequest('Start Time must be before End Time')
                
                # Verify time is a multiple of 5 min
                # start_time round up
                five_min = 5
                if avail_time['start_time'].minute % five_min > 0:
                    new_minute = avail_time['start_time'].minute + (five_min - avail_time['start_time'].minute % five_min)
                    new_hour = avail_time['start_time'].hour
                    if new_minute == 60:
                        new_hour = avail_time['start_time'].hour + 1
                        new_minute = 0
                    avail_time['start_time'] = globals()['time'](hour=new_hour, minute=new_minute)
                #end_time round down
                if avail_time['end_time'].minute % five_min > 0:
                    new_minute = avail_time['end_time'].minute - avail_time['end_time'].minute % five_min
                    avail_time['end_time'] = globals()['time'](hour=avail_time['end_time'].hour, minute=new_minute)

                # Localize to utc with current week
                today = datetime.now(tz.gettz(settings_data.timezone))
                delta = timedelta(days=-today.weekday() + DAY_OF_WEEK.index(avail_time['day_of_week']))
                # Temp_date is the day_of_week in availability on current local week
                temp_date = today + delta

                # Localize the provided start_time to UTC
                start_date_time_utc = datetime.combine(temp_date,avail_time['start_time'],\
                    tzinfo=tz.gettz(settings_data.timezone)).astimezone(tz.UTC)

                # Localize the provided end_time to UTC
                end_date_time_utc = datetime.combine(temp_date,avail_time['end_time'],\
                    tzinfo=tz.gettz(settings_data.timezone)).astimezone(tz.UTC)

                # Once availabilities are localized to UTC
                # If the availability spans one or two days, create time blocks for the given days accordingly
                if start_date_time_utc.weekday() == end_date_time_utc.weekday() or\
                    (start_date_time_utc.weekday() != end_date_time_utc.weekday() and end_date_time_utc.time() == globals()['time'](hour=0,minute=0)):
                    time_blocks = (
                        {
                            'startIdx': LookupBookingTimeIncrements.query.filter_by(start_time=start_date_time_utc.time()).first().idx, 
                            'endIdx': LookupBookingTimeIncrements.query.filter_by(end_time=end_date_time_utc.time()).first().idx, 
                            'weekday': DAY_OF_WEEK[start_date_time_utc.weekday()]
                        },
                    )
                else:
                    time_blocks = (
                        {
                            'startIdx': LookupBookingTimeIncrements.query.filter_by(start_time=start_date_time_utc.time()).first().idx, 
                            'endIdx': booking_increments[-1].idx, # end of day
                            'weekday': DAY_OF_WEEK[start_date_time_utc.weekday()]
                        },
                        {
                            'startIdx': booking_increments[0].idx, # start of day
                            'endIdx': LookupBookingTimeIncrements.query.filter_by(end_time=end_date_time_utc.time()).first().idx, 
                            'weekday': DAY_OF_WEEK[end_date_time_utc.weekday()]
                        },
                    )

                for block in time_blocks:
                    # Now, you loop through to store the booking window id into TelehealthStaffAvailability table.
                    for idx in range(block['startIdx'],block['endIdx'] + 1):
                        data['booking_window_id'] = idx
                        data['day_of_week'] = block['weekday']
                        data_in = TelehealthStaffAvailabilitySchema().load(data)
                        db.session.add(data_in)
                        
            #detect if practitoner has scheduled appointments outside of their new availability
            bookings = TelehealthBookings.query.filter_by(staff_user_id=user_id).filter(or_(
                TelehealthBookings.status == 'Accepted',
                TelehealthBookings.status == 'Pending'
                )).all()
            conflicts = []
            time_inc = LookupBookingTimeIncrements.query.all()
            for booking in bookings:
                staff_availability = db.session.execute(
                    select(TelehealthStaffAvailability).
                    filter(
                        TelehealthStaffAvailability.booking_window_id.in_([idx for idx in range (booking.booking_window_id_start_time_utc,booking.booking_window_id_end_time_utc + 1)]),
                        TelehealthStaffAvailability.day_of_week == DAY_OF_WEEK[booking.target_date_utc.weekday()],
                        TelehealthStaffAvailability.user_id == user_id
                        )
                ).scalars().all()
                
                # Make sure the full range of requested indices are found in staff_availability
                available_indices = {line.booking_window_id for line in staff_availability}
                requested_indices = {req_idx for req_idx in range(booking.booking_window_id_start_time_utc, booking.booking_window_id_end_time_utc + 1)}
                if not requested_indices.issubset(available_indices):
                    #booking is outside of the bounds of the new availability
                    start_time_utc = datetime.combine(
                        booking.target_date_utc,
                        time_inc[booking.booking_window_id_start_time_utc-1].start_time,
                        tzinfo=tz.UTC)

                    client = {**booking.client.__dict__}
                    practitioner = {**booking.practitioner.__dict__}
                    
                    conflicts.append({
                        'booking_id': booking.idx,
                        'target_date_utc': booking.target_date_utc,
                        'start_time_utc': start_time_utc.time(),
                        'status': booking.status,
                        'profession_type': booking.profession_type,
                        'client_location_id': booking.client_location_id,
                        'payment_method_id': booking.payment_method_id,
                        'status_history': booking.status_history,
                        'client': client,
                        'consult_rate': booking.consult_rate,
                        'charged': booking.charged
                    })
            
        else:
            #all availability is being removed, so all bookings are conflicts
            time_inc = LookupBookingTimeIncrements.query.all()
            conflicts = TelehealthBookings.query.filter_by(staff_user_id=user_id).all()
            for conflict in conflicts:
                    conflict.start_time_utc = time_inc[conflict.booking_window_id_start_time_utc-1].start_time
        db.session.commit()
        return {'conflicts': conflicts}

@ns.route('/queue/client-pool/')
class TelehealthGetQueueClientPoolApi(BaseResource):
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
class TelehealthQueueClientPoolApi(BaseResource):
    """
    This API resource is used to get, post, and delete the users in the queue.
    """
    # Multiple allowed
    __check_resource__ = False

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

        # Verify target date is client's local today or in the future 
        client_tz = request.parsed_obj.timezone
        target_date = datetime.combine(request.parsed_obj.target_date.date(), time(0, tzinfo=tz.gettz(client_tz)))
        client_local_datetime_now = datetime.now(tz.gettz(client_tz))
        if target_date.date() < client_local_datetime_now.date():
            raise BadRequest("Invalid target date")

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
            raise BadRequest(f'Location {location_id} does not exist.')

        # Verify payment method idx is valid from PaymentMethods
        # and that the payment method chosen has the user_id
        payment_id = request.parsed_obj.payment_method_id
        verified_payment_method = PaymentMethods.query.filter_by(user_id=user_id, idx=payment_id).one_or_none()
        if not verified_payment_method:
            raise BadRequest('Invalid payment method.')

        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

    @token_auth.login_required()
    @accepts(schema=TelehealthQueueClientPoolSchema, api=ns)
    @responds(api=ns, status_code=204)
    def delete(self, user_id):
        #Search for user by user_id in User table
        check_client_existence(user_id)
        appointment_in_queue = TelehealthQueueClientPool.query.filter_by(user_id=user_id,target_date=request.parsed_obj.target_date,profession_type=request.parsed_obj.profession_type).one_or_none()
        if appointment_in_queue:
            db.session.delete(appointment_in_queue)
            db.session.commit()


@ns.route('/bookings/details/<int:booking_id>')
class TelehealthBookingDetailsApi(BaseResource):
    """
    This API resource is used to get, post, and delete additional details about a telehealth boooking.
    Details may include a text description, images or voice recordings
    """
    # Cannot use check_resources, because there are no @accepts decorators on post() and put().
    # Those decorators are missing, because data is send as a form, not json. And that is
    # because files are being send.
    __check_resource__ = False

    @token_auth.login_required
    @responds(schema=TelehealthBookingDetailsGetSchema, api=ns, status_code=200)
    def get(self, booking_id):
        """
        Returns a list of details about the specified booking_id
        """
        #Check booking_id exists
        booking = TelehealthBookings.query.filter_by(idx=booking_id).one_or_none()
        if not booking:
            return

        #verify user trying to access details is the client or staff involved in scheulded booking
        # TODO allow access to Client Services?
        if booking.client_user_id != token_auth.current_user()[0].user_id \
            and booking.staff_user_id != token_auth.current_user()[0].user_id:

            raise Unauthorized('Only booking participants can view the details.')

        res = {'details': None,
                'images': [],
                'voice': None}

        #if there aren't any details saved for the booking_id, GET will return empty
        booking_dets = TelehealthBookingDetails.query.filter_by(booking_id = booking_id).first()
        if not booking_dets:
            return

        res['details'] = booking_dets.details

        #retrieve all files associated with this booking id
        fh = FileHandling()

        prefix = f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/'
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
        if not booking:
            raise BadRequest('Booking {booking_id} not found.')

        #only the client involved with the booking should be allowed to edit details
        if booking.client_user_id != token_auth.current_user()[0].user_id:
            raise Unauthorized('Only the client of this booking is allowed to edit details.')

        query = TelehealthBookingDetails.query.filter_by(booking_id=booking_id).one_or_none()
        if not query:
            raise BadRequest('Booking details you are trying to edit not found.')

        files = request.files #ImmutableMultiDict of key : FileStorage object

        #verify there's something to submit, if nothing, raise input error
        #if (not request.form.get('details') and len(files) == 0):
        if not ('details' in request.form or
                'images' in request.files or
                'voice' in request.files):
            return

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
                fh.delete_from_s3(prefix=f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/image')

            #if voice key is present, delete existing recording
            if 'voice' in files:
                fh.delete_from_s3(prefix=f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/voice')

            hex_token = secrets.token_hex(4)

            #upload images from request to s3
            for i, img in enumerate(files.getlist('images')):
                # validate file size - safe threashold (MAX = 10 mb)
                fh.validate_file_size(img, IMAGE_MAX_SIZE)
                # validate file type
                img_extension = fh.validate_file_type(img, ALLOWED_IMAGE_TYPES)

                s3key = f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/image_{hex_token}_{i}{img_extension}'
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

                s3key = f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/voice_{hex_token}_{i}{recording_extension}'
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
            raise BadRequest('Can not submit booking details without submitting a booking first.')

        details = TelehealthBookingDetails.query.filter_by(booking_id=booking_id).one_or_none()
        if details:
            raise BadRequest(f'Booking details for booking {booking_id} already exist.')

        #only the client involved with the booking should be allowed to edit details
        if booking.client_user_id != token_auth.current_user()[0].user_id:
            raise Unauthorized('Only the client of this booking is allowed to edit details.')

        #verify there's something to submit, if nothing, raise input error
        if not (form.get('details') or files):
            return {}, 204

        details = form.get('details', '')

        data = TelehealthBookingDetails(booking_id=booking_id, details=details)
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

                s3key = f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/image_{hex_token}_{i}{img_extension}'
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

                s3key = f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/voice_{hex_token}_{i}{recording_extension}'
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
        if not booking:
            return

        if booking.client_user_id != token_auth.current_user()[0].user_id:
            raise Unauthorized('Only the client of this booking is allowed to edit details.')

        details = TelehealthBookingDetails.query.filter_by(booking_id=booking_id).one_or_none()
        if not details:
            return

        db.session.delete(details)
        db.session.commit()

        #delete s3 resources for this booking id
        fh = FileHandling()
        fh.delete_from_s3(prefix=f'id{booking.client_user_id:05d}/meeting_files/booking{booking_id:05d}/')

@ns.route('/chat-room/access-token')
@ns.deprecated
@ns.doc(params={'client_user_id': 'Required. user_id of client participant.',
               'staff_user_id': 'Required. user_id of staff participant'})
class TelehealthChatRoomApi(BaseResource):
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
            raise BadRequest('Missing either staff or client user_id.')

        if user.user_id not in (staff_user_id, client_user_id):
            raise Unauthorized('Conversation access not allowed.')

        # get_chatroom helper function will take care of creating or bringing forward
        # previously created chat room and add user as a participant using their modobio_id
        # create_new=False so that a new chatroom is not provisioned. This may change in the future.
        twilio= Twilio()
        conversation = twilio.get_chatroom(staff_user_id = staff_user_id,
                                    client_user_id = client_user_id,
                                    participant_modobio_id = user.modobio_id,
                                    create_new=False)

        # API access for the user to specifically access this chat room
        twilio_credentials = twilio.grab_twilio_credentials()
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
class TelehealthAllChatRoomApi(BaseResource):
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
            raise Unauthorized('User requested must be logged in user')

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
            raise Unauthorized('Unsupported user type.')

        # add chat grants to a new twilio access token
        twilio = Twilio()
        twilio_credentials = twilio.grab_twilio_credentials()
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
class TelehealthBookingsCompletionApi(BaseResource):
    """
    API for completing bookings
    """
    @token_auth.login_required(user_type=('staff','client'))
    @responds(api=ns, status_code=200)
    def put(self, booking_id):
        """
        Complete the booking by:
        - send booking complete request to wheel
        - update booking status in TelehealthBookings
        - update twilio
        """
        booking = db.session.execute(select(TelehealthBookings).where(
            TelehealthBookings.idx == booking_id,
            TelehealthBookings.status == 'In Progress')).scalars().one_or_none()
        if not booking:
            raise BadRequest('Meeting does not exist or has not started yet.')

        current_user, _ = token_auth.current_user()

        # make sure the requester is one of the participants
        if current_user.user_id not in [booking.staff_user_id, booking.client_user_id]:
            raise Unauthorized('You must be a participant in this booking.')

        ##### WHEEL #####        
        # if booking.external_booking_id:
        #     wheel = Wheel()
        #     wheel.complete_consult(booking.external_booking_id)

        telehealth_utils.complete_booking(booking_id = booking.idx)

        return 

@ns.route('/bookings/transcript/<int:booking_id>/')
class TelehealthTranscripts(Resource):
    """
    Operations related to stored telehealth transcripts
    """
    @token_auth.login_required()
    @responds(api=ns, schema = TelehealthTranscriptsSchema, status_code=200)
    @ns.doc(params={'page': 'pagination index',
                'per_page': 'results per page'})
    def get(self, booking_id):
        """
        Retrieve messages from booking transscripts that have been stored on modobio's end
        """
        current_user, _ = token_auth.current_user()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        booking = TelehealthBookings.query.get(booking_id)

        if not booking:
            raise BadRequest('Meeting does not exist yet.')

        # make sure the requester is one of the participants
        if not any(current_user.user_id == uid for uid in [booking.client_user_id, booking.staff_user_id]):
            raise Unauthorized('You must be a participant in this booking.')

        # bring up the transcript messages from mongo db
        transcript = mongo.db.telehealth_transcripts.find_one({"_id": ObjectId(booking.chat_room.transcript_object_id)})


        # if there is any media in the transcript, generate a link to the download from the user's s3 bucket
        fh = FileHandling()

        payload = {'booking_id': booking_id, 'transcript': []}
        has_next = False
        for message_idx, message in enumerate(transcript.get('transcript',[])):
            # pagination logic: loop through all messages until we find the ones that are in the specified page, add those to the payload
            if message_idx <  (page-1) * per_page:
                continue
            elif message_idx >= (page * per_page):
                has_next = True
                break

            if message['media']:
                for media_idx, media in enumerate(message['media']):
                    _prefix = media['s3_path']
                    s3_link = fh.get_presigned_urls(prefix=_prefix)
                    media['media_link'] = [val for val in s3_link.values()][0]
                    transcript['transcript'][message_idx]['media'][media_idx] = media
            
            payload['transcript'].append(transcript['transcript'][message_idx])

        payload['_links'] =  {
                '_prev': url_for('api.telehealth_telehealth_transcripts', booking_id = booking_id, page = page - 1, per_page = per_page) if page > 1 else None,
                '_next': url_for('api.telehealth_telehealth_transcripts', booking_id = booking_id, page = page + 1, per_page = per_page) if has_next else None,
            }
        return payload
   
    @token_auth.login_required(dev_only=True)
    @responds(api=ns, status_code=200)
    def patch(self, booking_id):
        """
        **DEV only**

        Store booking transcripts for the booking_id supplied.
        This endpoint is only available in the dev environment. Normally booking transcripts are stored by a background process
        that is fired off following the completion of a booking. 

        Params
        ------
        booking_id

        Returns
        -------
        None
        """
        booking = TelehealthBookings.query.get(booking_id)

        if not booking:
            raise BadRequest('Meeting does not exist yet.')

        store_telehealth_transcript.delay(booking.idx)
                    
        return 

