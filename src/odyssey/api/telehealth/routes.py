from datetime import datetime, timedelta
import boto3
import jwt

from flask import current_app, request, jsonify
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey.api import api

from odyssey.api.telehealth.models import (
    TelehealthQueueClientPool,
    TelehealthStaffAvailability,
)
from odyssey.api.telehealth.schemas import (
    TelehealthQueueClientPoolSchema,
    TelehealthQueueClientPoolOutputSchema,
    TelehealthStaffAvailabilityOutputSchema
) 
from odyssey.utils.auth import token_auth
from odyssey.utils.errors import InputError, StaffEmailInUse, ClientEmailInUse, UnauthorizedUser
from odyssey.utils.misc import check_user_existence, check_client_existence, check_staff_existence, verify_jwt

from odyssey import db

ns = api.namespace('telehealth', description='Endpoint for telehealth requests.')

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
                        order_by(TelehealthStaffAvailability.start_time.asc()).all()
        
        monArr = []
        tueArr = [] 
        wedArr = []
        thuArr = [] 
        friArr = [] 
        satArr = []
        sunArr = []

        # Reorder to be Monday - Sunday
        for time in availability:
            if time.day_of_week == 'Monday':
                monArr.append(time)
            elif time.day_of_week == 'Tuesday':
                tueArr.append(time)
            elif time.day_of_week == 'Wednesday':
                wedArr.append(time)
            elif time.day_of_week == 'Thursday':
                thuArr.append(time)
            elif time.day_of_week == 'Friday':
                friArr.append(time)
            elif time.day_of_week == 'Saturday':
                satArr.append(time)
            elif time.day_of_week == 'Sunday':
                sunArr.append(time)
        
        orderedArr = [*monArr, *tueArr, *wedArr, *thuArr, *friArr, *satArr, *sunArr]

        payload = {}
        payload['availability'] = orderedArr
        
        return payload

    @token_auth.login_required
    @accepts(schema=TelehealthStaffAvailabilityOutputSchema, api=ns)
    @responds(schema=TelehealthStaffAvailabilityOutputSchema, api=ns, status_code=201)
    def post(self,user_id):
        """
        Returns the staff availability
        """
        check_staff_existence(user_id)

        availability = TelehealthStaffAvailability.query.filter_by(user_id=user_id).all()
        payload = {}
        if availability:
            for time in availability:
                db.session.delete(time)
        payload['availability'] = []

        if request.parsed_obj['availability']:
            avail = request.parsed_obj['availability']
            for time in avail:
                # end time must be after start time
                if time.start_time > time.end_time:
                    db.session.rollback()
                    raise InputError(status_code=405,message='Start Time must be before End Time')

                time.user_id = user_id
                db.session.add(time)
                payload['availability'].append(time)
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