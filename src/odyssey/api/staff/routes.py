
from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource
import json, calendar, copy
from flask.json import dumps
from datetime import date, time, datetime, timedelta, timezone
from dateutil import tz
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY, rrule
from dateutil.relativedelta import relativedelta

from odyssey import db
from odyssey.api import api
from odyssey.api.staff.models import StaffOperationalTerritories, StaffRoles, StaffRecentClients, StaffCalendarEvents
from odyssey.api.user.models import User, UserLogin, UserTokenHistory
from odyssey.utils.auth import token_auth, basic_auth
from odyssey.utils.errors import UnauthorizedUser, StaffEmailInUse, InputError
from odyssey.api.user.schemas import UserSchema, StaffInfoSchema
from odyssey.api.staff.schemas import (
    StaffOperationalTerritoriesNestedSchema,
    StaffProfileSchema, 
    StaffRolesSchema,
    StaffRecentClientsSchema,
    StaffTokenRequestSchema,
    StaffCalendarEventsSchema,
    StaffCalendarEventsUpdateSchema,
    StaffCalendarEventsGetSchema
)
from odyssey.utils.misc import check_staff_existence

ns = api.namespace('staff', description='Operations related to staff members')

@ns.route('/')
#@ns.doc(params={'firstname': 'first name to search',
#                'lastname': 'last name to search',
#                'user_id': 'user_id to search',
#                'email': 'email to search'})
class StaffMembers(Resource):
    """staff member class for creating, getting staff"""
    
    @token_auth.login_required
    #@responds(schema=StaffSearchItemsSchema(many=True), api=ns)
    @responds(schema=UserSchema(many=True), api=ns)
    def get(self):
        """returns list of staff members given query parameters"""                
        # These payload keys should be the same as what's indexed in 
        # the model.
        return User.query.filter_by(is_staff=True)

    
    @token_auth.login_required
    @accepts(schema=StaffProfileSchema, api=ns)
    @responds(schema=StaffProfileSchema, status_code=201, api=ns)     
    def post(self):
        """register a new staff member"""
        data = request.get_json() or {}
        #check if this email is already being used. If so raise 409 conflict error 
        staff = User.query.filter_by(email=data.get('email')).first()
        if staff:
            raise StaffEmailInUse(email=data.get('email'))

        ## TODO: rework Role suppression
        # system_admin: permisison to create staff admin.
        # staff_admin:  can create all other roles except staff/systemadmin
        # if data.get('is_system_admin'):
        #     raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user()[0].email} is unauthorized to create a system administrator role.")

        # if data.get('is_admin') and token_auth.current_user()[0].get_admin_role() != 'sys_admin':
        #     raise UnauthorizedUser(message=f"Staff member with email {token_auth.current_user()[0].email} is unauthorized to create a staff administrator role. \
        #                          Please contact system admin")
   
        #remove user data from staff data
        user_data = {'email': data['email'], 'password': data['password']}
        del data['email']
        del data['password']

        # Staff schema instance load from payload
        staff_schema = StaffProfileSchema()
        new_staff = staff_schema.load(data)

        db.session.add(new_staff)
        db.session.commit()

        user_data['user_id'] = new_staff.user_id
        new_user = UserSchema().load(user_data)
        
        db.session.add(new_user)
        db.session.commit()

        return new_staff

@ns.route('/roles/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class UpdateRoles(Resource):
    """
    View and update roles for staff member with a given user_id
    """
    @token_auth.login_required
    @accepts(schema=StaffInfoSchema, api=ns)
    @responds(status_code=201, api=ns)   
    def post(self, user_id):
        staff_user, _ = token_auth.current_user()

        # staff are only allowed to edit their own info
        if staff_user.user_id != user_id:
            raise UnauthorizedUser(message="")
        
        data = request.get_json()
        staff_roles = db.session.query(StaffRoles.role).filter(StaffRoles.user_id==user_id).all()
        staff_roles = [x[0] for x in staff_roles]
        staff_role_schema = StaffRolesSchema()

        # loop through submitted roles, add role if not already in db
        for role in data['access_roles']:
            if role not in staff_roles:
                db.session.add(staff_role_schema.load(
                    {'user_id': user_id, 
                    'role': role}))
        
        db.session.commit()
        
        return

    @token_auth.login_required
    @responds(schema=StaffRolesSchema(many=True), status_code=200, api=ns)   
    def get(self, user_id):
        """
        Get staff roles
        """
        staff_user, _ = token_auth.current_user()
       
        staff_roles = StaffRoles.query.filter_by(user_id = user_id)

        return staff_roles

@ns.route('/operational-territories/<int:user_id>/')
@ns.doc(params={'user_id': 'User ID number'})
class OperationalTerritories(Resource):
    """
    View and update operational territories for staff member with a given user_id
    """
    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffOperationalTerritoriesNestedSchema, api=ns)
    @responds(schema = StaffOperationalTerritoriesNestedSchema, status_code=201, api=ns)   
    def post(self, user_id):
        staff_user, _ = token_auth.current_user()

        # staff are only allowed to edit their own info
        if staff_user.user_id != user_id:
            raise UnauthorizedUser(message="")
        data = request.parsed_obj
        # current operational territories
        current_territories = db.session.query(
                        StaffOperationalTerritories.role_id, StaffOperationalTerritories.operational_territory_id
                        ).filter(
                            StaffOperationalTerritories.user_id==user_id
                        ).all()

        # ids of current roles held by staff member             
        current_role_ids = db.session.query(
                        StaffRoles.idx
                        ).filter(
                            StaffRoles.user_id == user_id
                        ).all()
        current_role_ids = [x[0] for x in current_role_ids]

        for territory in data["operational_territories"]:
            # check if role-territory combination already exists. if so, skip it
            if not (territory.role_id, territory.operational_territory_id) in current_territories:
                # ensure role_id is assigned to this staff member
                if territory.role_id in current_role_ids:
                    territory.user_id = user_id
                    db.session.add(territory)
                else:
                    db.session.rollback()
                    raise UnauthorizedUser(message="the staff member does not have this role")

        db.session.commit()
        
        # current operational territories
        current_territories = db.session.query(
                        StaffOperationalTerritories.role_id, StaffOperationalTerritories.operational_territory_id
                        ).filter(
                            StaffOperationalTerritories.user_id==user_id
                        ).all()

        return {"operational_territories": current_territories}

    @token_auth.login_required
    @responds(schema = StaffOperationalTerritoriesNestedSchema, status_code=200, api=ns)   
    def get(self, user_id):
        """
        Responds with current operational territories for each role a staff user
        has assumed
        """
        # current operational territories
        current_territories = db.session.query(
                        StaffOperationalTerritories.role_id, StaffOperationalTerritories.operational_territory_id
                        ).filter(
                            StaffOperationalTerritories.user_id==user_id
                        ).all()
        return {"operational_territories": current_territories}

    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffOperationalTerritoriesNestedSchema, api=ns)
    @responds(schema = StaffOperationalTerritoriesNestedSchema, status_code=204, api=ns)   
    def delete(self, user_id):
        """
        Uses the same payload as the POST request on this endpoint to delete 
        entries to the operational territories database.
        """
        data = request.parsed_obj

        for territory in data["operational_territories"]:
            StaffOperationalTerritories.query.filter_by(
                                                    user_id=user_id
                                                ).filter_by(
                                                    operational_territory_id = territory.operational_territory_id
                                                ).filter_by(
                                                    role_id = territory.role_id
                                                ).delete()
        
        db.session.commit()

        return 
    

@ns.route('/recentclients/')
class RecentClients(Resource):
    """endpoint related to the staff recent client feature"""
    
    @token_auth.login_required
    @responds(schema=StaffRecentClientsSchema(many=True), api=ns)
    def get(self):
        """get the 10 most recent clients a staff member has loaded"""
        return StaffRecentClients.query.filter_by(user_id=token_auth.current_user()[0].user_id).all()

""" Staff Token Endpoint """

@ns.route('/token/')
class StaffToken(Resource):
    """create and revoke tokens"""
    @ns.doc(security='password')
    @basic_auth.login_required(user_type=('staff',), email_required=False)
    @responds(schema=StaffTokenRequestSchema, status_code=201, api=ns)
    def post(self):
        """generates a token for the 'current_user' immediately after password authentication"""
        user, user_login = basic_auth.current_user()
        if not user:
            return 401
        # bring up list of staff roles
        access_roles = db.session.query(
                                StaffRoles.role
                            ).filter(
                                StaffRoles.user_id==user.user_id
                            ).all()

        access_token = UserLogin.generate_token(user_type='staff', user_id=user.user_id, token_type='access')
        refresh_token = UserLogin.generate_token(user_type='staff', user_id=user.user_id, token_type='refresh')

        db.session.add(UserTokenHistory(user_id=user.user_id, 
                                        refresh_token=refresh_token,
                                        event='login',
                                        ua_string = request.headers.get('User-Agent')))
        db.session.commit()

        return {'email': user.email, 
                'firstname': user.firstname, 
                'lastname': user.lastname, 
                'token': access_token,
                'refresh_token': refresh_token,
                'user_id': user.user_id,
                'access_roles': [item[0] for item in access_roles],
                'email_verified': user.email_verified}


    @ns.doc(security='password')
    @ns.deprecated
    @token_auth.login_required(user_type=('staff',))
    def delete(self):
        """
        Deprecated 11.23.20..does nothing now
        """
        return '', 200

@ns.route('/calendar/<int:user_id>/')
class StaffCalendarEventsRoute(Resource):
    """
    Endpoint to manage professional's (staff) calendar events
    """
    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffCalendarEventsSchema, api=ns)
    @responds(schema=StaffCalendarEventsSchema, status_code=201, api=ns)
    def post(self, user_id):
        """
        Create a new calendar event 
        """
        data = request.parsed_obj
        data.user_id = user_id
        
        if data.end_date:
            date_delta = data.end_date - data.start_date
            if date_delta.total_seconds() < 0:
                raise InputError(422, 'Event end date must be later than start date or null')

        if data.all_day:
            data.start_time = time(hour=0, minute=0, second=0,  tzinfo=tz.tzlocal())
            data.end_time = time(hour=23, minute=59, second=59, tzinfo=tz.tzlocal())
            
            if data.recurring:
                if not data.recurrence_type:
                    raise InputError(422, 'Recurring events require recurrence type')    
            else:
                data.recurrence_type = None
                if not data.end_date:
                    raise InputError(422, 'This event requires an end date')

            data.duration = timedelta(days=1)
                
        else:
            data.start_time = data.start_time.replace(tzinfo=tz.tzlocal())
            start = datetime.combine(data.start_date, data.start_time)
            data.end_time = data.end_time.replace(tzinfo=tz.tzlocal())
            if data.recurring:
                end = datetime.combine(data.start_date, data.end_time)
                if not data.recurrence_type:
                    raise InputError(422, 'Recurring events require recurrence type')  
            else:
                data.recurrence_type = None
                if not data.end_date:
                    raise InputError(422, 'This event requires an end date')
                end = datetime.combine(data.end_date, data.end_time)

            #Event's start time must come before end time
            delta = end - start
            if delta.total_seconds() < 0:
                raise InputError(422, 'Start of event must be earlier than End of event')
            
            data.duration = delta
        
        if (data.recurrence_type == 'Monthly' and data.start_date.day > 28) or (data.recurrence_type == 'Yearly' and data.start_date.month == 2 and data.start_date.day > 28):
            data.warning = f'Some months have less than {data.start_date.day} days. Those months, the occurrence will fall on the last day of the month'

        data.timezone = data.start_time.tzname()
        db.session.add(data)
        db.session.commit()
        return data


    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffCalendarEventsUpdateSchema, api=ns)
    @responds(schema=StaffCalendarEventsUpdateSchema, status_code=200, api=ns)
    def put(self, user_id):
        """
        Update a calendar event

        expects 
        {
            "revised_event_schema":{nested StaffCalendarEventsSchema},
            "entire_series": bool,
            "previous_start_date": datetime.date,
            "event_to_update_idx": int
        }
        """
        data = request.parsed_obj
        updated_event = data['revised_event_schema']
        updated_event_dict = request.json['revised_event_schema']
        entire_series = data['entire_series']
        idx = data['event_to_update_idx']
        prev_start_date = data['previous_start_date']

        #prepare edited event
        updated_event.user_id = user_id
        updated_event.idx = idx
       
        #Some validations
        query = StaffCalendarEvents.query.filter_by(idx=idx).one_or_none()
        if query:
            if updated_event.end_date:
                date_delta = updated_event.end_date - updated_event.start_date
                if date_delta.total_seconds() < 0:
                    raise InputError(422, 'Event end date must be later than start date or null')

            if updated_event.all_day:
                updated_event.start_time = time(hour=0, minute=0, second=0, tzinfo=tz.tzlocal())
                updated_event.end_time = time(hour=23, minute=59, second=59, tzinfo=tz.tzlocal())
            
                if updated_event.recurring:
                    if not updated_event.recurrence_type:
                        raise InputError(422, 'Recurring events require recurrence type')
                else:
                    updated_event.recurrence_type = None
                    if not updated_event.end_date:
                        raise InputError(422, 'This event requires an end date')

                updated_event.duration = timedelta(days=1)
            else:
                updated_event.start_time = updated_event.start_time.replace(tzinfo=tz.tzlocal())
                start = datetime.combine(updated_event.start_date, updated_event.start_time)
                updated_event.end_time = updated_event.end_time.replace(tzinfo=tz.tzlocal())
                if updated_event.recurring:
                    end = datetime.combine(updated_event.start_date, updated_event.end_time)
                    if not updated_event.recurrence_type:
                        raise InputError(422, 'Recurring events require recurrence type')  
                else:
                    updated_event.recurrence_type = None
                    if not updated_event.end_date:
                        raise InputError(422, 'This event requires an end date')
                    end = datetime.combine(updated_event.end_date, updated_event.end_time)

                #Event's start time must come before end time
                delta = end - start
                if delta.total_seconds() < 0:
                    raise InputError(422, 'Start of event must be earlier than End of event')
                
                updated_event.duration = delta
            
            if (updated_event.recurrence_type == 'Monthly' and updated_event.start_date.day > 28) or (updated_event.recurrence_type == 'Yearly' and updated_event.start_date.month == 2 and updated_event.start_date.day > 28):
                updated_event.warning = f'Some months have less than {updated_event.start_date.day} days. Those months, the occurrence will fall on the last day of the month'

            updated_event.timezone = updated_event.start_time.tzname()

            #Inputs validated, now edit db entry
            if entire_series or (not entire_series and not query.recurring):
                query.update(updated_event_dict)
            
            else: #recurring event & editing one occurence
                #updated event is a lone, new event (can't be recurring)
                updated_event.recurring = False
                updated_event.recurrence_type = None
                db.session.add(updated_event)

                #create a copy of current query event, and have it start after updated occurence
                new_recurrence = StaffCalendarEvents()
                new_recurrence.user_id = query.user_id
                new_recurrence.all_day = query.all_day
                new_recurrence.availability_status = query.availability_status
                new_recurrence.description = query.description
                new_recurrence.location = query.location
                new_recurrence.duration = query.duration
                new_recurrence.recurring = query.recurring
                new_recurrence.recurrence_type = query.recurrence_type
                new_recurrence.start_time = query.start_time
                new_recurrence.end_time = query.end_time
                new_recurrence.end_date = query.end_date
                new_recurrence.timezone = query.timezone

                if query.recurrence_type == "Yearly":
                    recurrence_delta = relativedelta(years=1)
                elif query.recurrence_type == "Monthly":
                    recurrence_delta = relativedelta(months=1)
                elif query.recurrence_type == "Weekly":
                    recurrence_delta = relativedelta(weeks=1)
                else:
                    recurrence_delta = relativedelta(days=1)

                new_recurrence.start_date = prev_start_date + recurrence_delta
                db.session.add(new_recurrence)

                query.end_date = prev_start_date - timedelta(days=1)

        else:
            raise InputError(204, 'No such event')
        db.session.commit()
        return data


    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffCalendarEventsGetSchema, api=ns)
    @responds(schema=StaffCalendarEventsSchema(many=True), status_code=200, api=ns)
    def get(self, user_id):
        """
        View all calendar events
        Accepts optional parameters year, month, day to filter by date_start field
        if no year is provided, year defaults to current year.

        Ignores all inputs other than ints for args
        """
        #If no year provided, the year deafults to current year
        year = request.parsed_obj.get('year', datetime.now().year)
        month = request.parsed_obj.get('month')
        day = request.parsed_obj.get('day')
        
        #if the resquest inludes a day but not a month, the month defaults to current month
        if day:
            if not month:
                month = datetime.now().month
            #verify full date is a valid date
            try:
                datetime(year,month,day)
            except ValueError:
                raise InputError(422, "Invalid Date")

        query_set = set(StaffCalendarEvents.query.filter_by(user_id=user_id).order_by(StaffCalendarEvents.start_date.desc()).all())
        new_query = query_set.copy()
        
        #Sort through all saved events that match the requested year, month or day
        for event in query_set:
            if event.recurring:
                if event.start_date.year > year:
                    new_query.discard(event)
                elif event.end_date and event.end_date.year < year:
                    new_query.discard(event)
            else:
                if event.start_date.year != year and not event.end_date.year <= year:
                    new_query.discard(event)
        
        query_set = new_query.copy()
        if month:
            last_day_of_month = calendar.monthrange(year,month)[1]
            for event in query_set:
                if event.recurring:
                    check_date_2 = datetime(year,month,1).date()
                    try:
                        check_date = datetime(year,month,event.start_date.day).date()
                    except ValueError:
                        check_date = datetime(year,month,last_day_of_month).date()
                    
                    if check_date < event.start_date:
                        new_query.discard(event)
                    elif event.end_date and check_date_2 > event.end_date:
                        new_query.discard(event)
                else:
                    check_date_2 = datetime(year,month,1).date()
                    check_date_1 = datetime(year,month,last_day_of_month).date()
                    if (event.start_date.month != month and event.start_date == event.end_date) or event.end_date  < check_date_2 or event.start_date > check_date_1:
                        new_query.discard(event)       
        
        query_set = new_query.copy()
        if day:
            for event in query_set:
                if event.recurring:
                    date_check = datetime(year,month,day).date()
                    if date_check < event.start_date: 
                        new_query.discard(event)
                    elif event.end_date and date_check > event.end_date:
                        new_query.discard(event)
                else:
                    if event.start_date.day != day and event.end_date < datetime(year,month,day).date():
                        new_query.discard(event)
        
        payload = []
        for event in new_query:
            if event.recurring:
                #produce set of occurrences
                week_day = event.start_date.weekday()
                if year and not month and not day:
                    occurrence = copy.deepcopy(event)
                    if event.recurrence_type == 'Yearly':
                        if event.start_date.month == 2 and event.start_date.day > 28:
                            occurrence.start_date = datetime(year,event.start_date.month,28).date()
                        else:
                            occurrence.start_date = datetime(year,event.start_date.month,event.start_date.day).date()
                        payload.append(occurrence)
                    elif event.recurrence_type == 'Monthly':
                        if event.start_date.day <= 28:
                            dt_start = datetime(year,1,event.start_date.day)
                            mylist = list(rrule(MONTHLY,count=12,dtstart=dt_start))
                        elif event.start_date.day == 31:
                            #if start date is 31, use last day of month for all months
                            mylist=[]
                            for _month in range(1,13):
                                mylist.append(datetime(year,_month,calendar.monthrange(year,_month)[1]))
                        else:
                            #if start date is 30 or 29, use last day only for feb 
                            dt_start = datetime(year,1,event.start_date.day)
                            mylist = list(rrule(MONTHLY,count=11,dtstart=dt_start))
                            #last day of feb = calendar.monthrange(year,2)[1]
                            mylist.append(datetime(year,2,calendar.monthrange(year,2)[1]))                    
                        for _day in mylist:
                            if _day.date() >= event.start_date:
                                if not event.end_date or _day.date() <= event.end_date:
                                    occurrence.start_date = _day.date()
                                    payload.append(occurrence)
                                    occurrence = copy.deepcopy(event)                       
                    elif event.recurrence_type == 'Weekly':
                        #count=53 for weeks in a year rounded up
                        mylist = list(rrule(WEEKLY,count=53,byweekday=(week_day),dtstart=datetime(year,1,1)))
                        for _day in mylist:
                            if _day.date() >= event.start_date and _day.year == year:
                                if not event.end_date or _day.date() <= event.end_date:
                                    occurrence.start_date = _day.date()
                                    payload.append(occurrence)
                                    occurrence = copy.deepcopy(event)
                    elif event.recurrence_type == 'Daily':
                        #count=366 for days in a year, considering leap years
                        mylist = list(rrule(DAILY,count=366,dtstart=datetime(year,1,1)))
                        for _day in mylist:
                            if _day.date() >= event.start_date and _day.year == year:
                                if not event.end_date or _day.date() <= event.end_date:
                                    occurrence.start_date = _day.date()
                                    payload.append(occurrence)
                                    occurrence = copy.deepcopy(event)

                elif year and month and not day:
                    occurrence = copy.deepcopy(event)
                    if event.recurrence_type == 'Yearly':
                        if event.start_date.month == month:
                            if month == 2 and event.start_date.day > last_day_of_month:
                                occurrence.start_date = datetime(year,month,last_day_of_month).date()
                            else:
                                occurrence.start_date = datetime(year,month,event.start_date.day).date()
                            payload.append(occurrence)
                    elif event.recurrence_type == 'Monthly':
                        if event.start_date.day > last_day_of_month:
                            occurrence.start_date = datetime(year,month,last_day_of_month).date()
                        else:
                            occurrence.start_date = datetime(year,month,event.start_date.day).date()
                        payload.append(occurrence)
                    elif event.recurrence_type == 'Weekly':
                        #count = 5 as the max # of possible 'any week day' in a month
                        mylist = list(rrule(WEEKLY,count=5,byweekday=(week_day),dtstart=datetime(year,month,1)))
                        for _day in mylist:
                            if _day.month == month and _day.date() >= event.start_date:
                                if not event.end_date or _day.date() <= event.end_date:
                                    occurrence.start_date = _day.date()
                                    payload.append(occurrence)
                                    occurrence = copy.deepcopy(event)
                    elif event.recurrence_type == 'Daily':
                        mylist = list(rrule(DAILY,count=last_day_of_month,dtstart=datetime(year,month,1)))
                        for _day in mylist:
                            if _day.date() >= event.start_date:
                                if not event.end_date or _day.date() <= event.end_date:
                                    occurrence.start_date = _day.date()
                                    payload.append(occurrence)
                                    occurrence = copy.deepcopy(event)
                
                else:
                    specified_date = datetime(year,month,day).date()
                    occurrence = copy.deepcopy(event)
                    if event.recurrence_type == 'Yearly':
                        if event.start_date.month == month and event.start_date.day == day:
                            occurrence.start_date = specified_date
                            payload.append(occurrence)
                        elif event.start_date.month == month and month == 2 and event.start_date.day > last_day_of_month and specified_date.day == last_day_of_month:
                            occurrence.start_date = specified_date
                            payload.append(occurrence)
                    elif event.recurrence_type == 'Monthly':
                        if specified_date.day == event.start_date.day:
                            occurrence.start_date = specified_date
                            payload.append(occurrence)
                        elif event.start_date.day > last_day_of_month and specified_date.day == last_day_of_month:
                            occurrence.start_date = datetime(year,month,last_day_of_month)
                            payload.append(occurrence)
                    elif event.recurrence_type == 'Weekly':
                        if week_day == datetime(year,month,day).weekday():
                            occurrence.start_date = specified_date
                            payload.append(occurrence)
                    elif event.recurrence_type == 'Daily':
                        occurrence = copy.deepcopy(event)
                        occurrence.start_date = specified_date
                        payload.append(occurrence)

            else:
                #non recurring event but spans more than 1 day (semi recurring)
                if year and month and day and event.duration > timedelta(days=1):
                    if datetime(year,month,day).date() == event.start_date:
                        event.end_time = time(23,59,59)
                    elif datetime(year,month,day).date() == event.end_date:
                        event.start_time = time(00,00)
                    else:
                        event.start_time = time(00,00)
                        event.end_time = time(23,59,59)
                payload.append(event)
        
        return payload


    @token_auth.login_required(user_type=('staff_self',))
    @accepts(schema=StaffCalendarEventsUpdateSchema(only=("entire_series", "event_to_update_idx", "previous_start_date")), api=ns)
    def delete(self, user_id):
        """
        Delete events
        """
        entire_series = request.parsed_obj['entire_series']
        idx = request.parsed_obj['event_to_update_idx']
        prev_start_date = request.parsed_obj['previous_start_date']

        query = StaffCalendarEvents.query.filter_by(idx=idx).one_or_none()

        if query:
            if query.recurring and not entire_series:
                #create a copy of current query event, and have it start after updated occurence
                new_recurrence = StaffCalendarEvents()
                new_recurrence.user_id = query.user_id
                new_recurrence.all_day = query.all_day
                new_recurrence.availability_status = query.availability_status
                new_recurrence.description = query.description
                new_recurrence.location = query.location
                new_recurrence.duration = query.duration
                new_recurrence.recurring = query.recurring
                new_recurrence.recurrence_type = query.recurrence_type
                new_recurrence.start_time = query.start_time
                new_recurrence.end_time = query.end_time
                new_recurrence.end_date = query.end_date
                new_recurrence.timezone = query.timezone

                if query.recurrence_type == "Yearly":
                    recurrence_delta = relativedelta(years=1)
                elif query.recurrence_type == "Monthly":
                    recurrence_delta = relativedelta(months=1)
                elif query.recurrence_type == "Weekly":
                    recurrence_delta = relativedelta(weeks=1)
                else:
                    recurrence_delta = relativedelta(days=1)

                new_recurrence.start_date = prev_start_date + recurrence_delta
                db.session.add(new_recurrence)

                query.end_date = prev_start_date - timedelta(days=1)

            else:
                db.session.delete(query)
        
        else: 
            raise InputError(204, 'No such event')

        db.session.commit()
        return ("Event Deleted", 200)