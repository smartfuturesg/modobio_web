from dateutil import parser
import requests

from flask import current_app
from sqlalchemy import select

from odyssey import db
from odyssey.api.lookup.models import LookupBookingTimeIncrements, LookupOrganizations
from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation
from odyssey.utils.errors import GenericThirdPartyError, InputError, UnknownError


class Wheel:
    """ A class for performing common wheel API calls """

    def __init__(self):
        """ 
        Prepare the wheel object
        """

        self.wheel_api_token = current_app.config.get('WHEEL_API_TOKEN')
        self.wheel_md_consult_rate = current_app.config['WHEEL_MD_CONSULT_RATE']
        self.url_base = "https://sandbox-api.enzymeondemand.com"

    def available_timeslots(self, target_time_range, clinician_id=''):
        """
        Query wheel's API to find timeslots for a specific datetime range.
        Wheel URI: /v1/consult_rates/<consult_rate>/timeslots


        Params
        ------
        target_time_range: (datetime, datetime)
            tuple containing the start and end datetimes of the target booking window in UTC

        clinician_id
            optional wheel_clinician_id of the clinician
        
        Returns
        -------
        dict
        of available time increments: {user_id : [booking_availability_ids]}
  
        
        TODO: add practitioner sex to query when wheel has implemented the feature
        """
        # skip wheel during testing
        if current_app.config['TESTING']:
            return {}
             
        target_start_datetime_utc, target_end_datetime_utc =  target_time_range

        time_inc = LookupBookingTimeIncrements.query.all()
        
        start_time_idx_dict = {item.start_time.isoformat() : item.idx for item in time_inc} # {datetime.time: booking_availability_id}
        wheel_practitioner_availabilities = {} # {target_date_utc: {user_id : [booking_availability_ids]}}
        loaded_wheel_practitioners = Wheel.clinician_ids(key='wheel_clinician_id') # {wheel_uid : modobio_user_id}
        
        # wheel_practitioner_availabilities stores utc times which may differ from the client's timezone
        # availabilities may be between two days in utc 
        wheel_practitioner_availabilities[target_start_datetime_utc.date()] = {}
        if target_start_datetime_utc.date() != target_end_datetime_utc.date():
            wheel_practitioner_availabilities[target_end_datetime_utc.date()] = {}

        page = 1
        uri = self.url_base+ f"/v1/consult_rates/{self.wheel_md_consult_rate}/timeslots"
        while page:
            dat = requests.get(
                uri,
                headers={'x-api-key': self.wheel_api_token,
                'Content-Type': 'application/json'},
                params={'start': target_start_datetime_utc.isoformat(), 
                        'end': target_end_datetime_utc.isoformat(), 
                        'page': page, 
                        'clinician_id': clinician_id}
            )
            
            try:
                dat.raise_for_status()
            except Exception as e:
                raise GenericThirdPartyError(status_code = dat.status_code, message=dat.json())
                
            results = dat.json()
            page = (page + 1 if results['links'].get('next') else False)
            for availability in results['data']:
                
                start_at = parser.isoparse(availability['start_at'])
                start_at_idx = start_time_idx_dict.get(start_at.time().strftime('%H:%M:%S'))
                availability_idx_range = [i for i in range(start_at_idx, start_at_idx + 4)]
                target_date_utc = start_at.date()

                for practitioner in availability['clinicians']:
                    if not wheel_practitioner_availabilities[target_date_utc].get(loaded_wheel_practitioners[practitioner['id']]):
                        wheel_practitioner_availabilities[target_date_utc][loaded_wheel_practitioners[practitioner['id']]]  = availability_idx_range
                        loaded_wheel_practitioners[practitioner['id']]
                    else:
                        wheel_practitioner_availabilities[target_date_utc][loaded_wheel_practitioners[practitioner['id']]].extend(availability_idx_range)
        
        return wheel_practitioner_availabilities

    @staticmethod
    def clinician_ids(key='user_id'):
        """
        returns dictionary:
            keys: user_id or wheel_clinician_id
            values: wheel_clinician_id or user_id 
        """
        if key not in ('user_id', 'wheel_clinician_id'):
            raise InputError(message='invalid request for wheel clinician id dictionary key')

        query = db.session.execute(
            select(PractitionerOrganizationAffiliation
            ).join(LookupOrganizations, LookupOrganizations.idx == PractitionerOrganizationAffiliation.organization_idx
            ).where(LookupOrganizations.org_name == 'Wheel')
        ).scalars().all()

        if key == 'user_id':
            return {item.user_id : item.affiliate_user_id for item in query}

        else:
            return {item.affiliate_user_id : item.user_id for item in query}
