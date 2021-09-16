import random
from typing import Tuple
from dateutil import parser
from flask_restx.fields import Date, DateTime

from odyssey.api.staff.models import StaffOperationalTerritories, StaffProfile, StaffRoles
from io import BytesIO
from PIL import Image
import requests
import uuid

from flask import current_app
from sqlalchemy import select
from werkzeug.datastructures import FileStorage

from odyssey import db
from odyssey.api.lookup.models import LookupBookingTimeIncrements, LookupOrganizations, LookupTerritoriesOfOperations
from odyssey.api.practitioner.models import PractitionerCredentials, PractitionerOrganizationAffiliation
from odyssey.api.telehealth.models import TelehealthBookings, TelehealthStaffSettings
from odyssey.api.user.models import User, UserLogin, UserProfilePictures
from odyssey.utils.errors import GenericThirdPartyError, InputError
from odyssey.utils.constants import ALLOWED_IMAGE_TYPES, ALPHANUMERIC, IMAGE_DIMENSIONS, IMAGE_MAX_SIZE
from odyssey.utils.misc import FileHandling


class Wheel:
    """ A class for performing common wheel API calls """

    def __init__(self):
        """ 
        Prepare the wheel object
        """

        self.wheel_api_token = current_app.config.get('WHEEL_API_TOKEN')
        self.wheel_md_consult_rate = current_app.config['WHEEL_MD_CONSULT_RATE']
        self.url_base = "https://sandbox-api.enzymeondemand.com"
        self.wheel_org_idx = db.session.execute(select(LookupOrganizations.idx).where(LookupOrganizations.org_name == 'Wheel')).scalars().one_or_none()


    def available_timeslots(self, target_time_range: Tuple[DateTime, DateTime], location_id: int, clinician_id: str = ''):
        """
        Query wheel's API to find timeslots for a specific datetime range.
        Wheel URI: /v1/consult_rates/<consult_rate>/timeslots


        Params
        ------
        target_time_range: (datetime, datetime)
            tuple containing the start and end datetimes of the target booking window in UTC
        
        location_id:
            where the client is located. Converted to state abbreviation for wheel request

        clinician_id
            optional wheel_clinician_id of the clinician
        
        Returns
        -------
        dict
        of available time increments: {user_id : [booking_availability_ids]}
  
        
        TODO: add practitioner sex to query when wheel has implemented the feature
        """

        # use location_id to get the state abbreviation
        state = db.session.execute(select(LookupTerritoriesOfOperations.sub_territory_abbreviation).where(LookupTerritoriesOfOperations.idx==location_id)).scalar_one_or_none()
             
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
                        'clinician_id': clinician_id,
                        'state': state}
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


    def make_booking_request(self, staff_user_id: int, client_user_id: int, location_id: int, booking_id: int, booking_start_time: DateTime):
        """
        Make request to wheel for booking using the provided user_id
        
        Responds
        --------
        (booking_external_id: str, consult_url_deeplink: str)
        """

        # bring up staff user. Get wheel id
        staff_user = db.session.execute(select(User).where(User.user_id == staff_user_id)).scalar_one_or_none()

        # bring up client, get modobio_id
        client_user = db.session.execute(select(User).where(User.user_id == client_user_id)).scalar_one_or_none()
        
        # use location_id to get the state abbreviation
        state = db.session.execute(select(LookupTerritoriesOfOperations.sub_territory_abbreviation).where(LookupTerritoriesOfOperations.idx==location_id)).scalar_one_or_none()

        # get practitioner wheel id
        wheel_clinician_id = db.session.execute(select(PractitionerOrganizationAffiliation.affiliate_user_id
        ).where(PractitionerOrganizationAffiliation.user_id == staff_user_id)).scalar_one_or_none()

        # booking_external_id 
        booking_external_id = uuid.uuid4()

        consult_url_deeplink = f'https://{current_app.config["DOMAIN_NAME"]}/telehealth?clientId={client_user_id}&bookingId={booking_id}'

        payload =  {
            "consult_id" : str(booking_external_id),
            "consult_url": consult_url_deeplink,
            "patient_id": client_user.modobio_id,
            "state": state,
            "consult_rate_id": self.wheel_md_consult_rate,
            "appointment": {
                "clinician_id" : wheel_clinician_id,
                "start_at": booking_start_time.isoformat()
            }
        }

        url = self.url_base+ f"/v1/consults"

        response = requests.post(
                url,
                headers={'x-api-key': self.wheel_api_token,
                'Content-Type': 'application/json'},
                json = payload
            )

        # errors with booking a consultation are fatal. 
        # TODO: Consider making this a recoverable situation by retrying
        try:
            response.raise_for_status()
        except Exception as e:
            raise GenericThirdPartyError(status_code = response.status_code, message=response.json())

        return booking_external_id, consult_url_deeplink
        
    def physician_roster(self):
        """
        responds with wheel's full clinician roster
        """

        clinicians = []
        page = 1
        uri = self.url_base + "/v1/clinicians"
        while page:
            dat = requests.get(
                uri,
                headers={'x-api-key': self.wheel_api_token,
                'Content-Type': 'application/json'},
                params={'page': page}
            )
            results = dat.json()
            page = (page + 1 if results['links'].get('next') else False)
            clinicians.extend(results.get('data'))
        
        return clinicians
    
    def get_wheel_physician(self, affiliate_id):
        """
        Bring up the wheel clinician using their affiliate_id 
        """
        user = db.session.execute(
            select(
                User, PractitionerOrganizationAffiliation
            ).join(
                PractitionerOrganizationAffiliation, PractitionerOrganizationAffiliation.user_id == User.user_id
            ).where(
                PractitionerOrganizationAffiliation.organization_idx == self.wheel_org_idx,
                PractitionerOrganizationAffiliation.affiliate_user_id == affiliate_id
            )
        ).scalar_one_or_none()

        return user
    
    def update_modobio_physician_roster(self):
        """
        Add or update wheel clinicians in the modobio system. If new clinician is found, create a new user account

        'email', 
        'status': 'active' or otherwise, 
        'name': needs to be split into first and last name, 
        'practitioner_type': 'md', 'np'
        'timezone': IANA Tzones
        'sex': 'Male' or otherwise fem
        'npi':
        'license_info'['ca']['expires_at']/['license_number']
        'photo': ** Not sure what to do here, download and then upload to s3?
        'about': bio if we will have one

        Must Populate:
        User: generic info and sex
        TelehealthStaffSettings: timezone
        UserLogin (if user is new, create a password) TODO: send email? password 
        UserProfilePictures: profile pic from wheel if they provide one
        StaffProfile: bio, memebrsince (added automatically by db)
        """

        roles_mapper = {'md': 'medical_doctor', 'np': 'nurse_practitioner'}
        full_roster = self.physician_roster()
        
        wheel_physician_ids = Wheel.clinician_ids(key='wheel_clinician_id')

        operational_territories_mapper = db.session.execute(
            select(LookupTerritoriesOfOperations.sub_territory_abbreviation, LookupTerritoriesOfOperations.idx)).all()
        operational_territories_mapper = {item[0].lower() : item[1] for item in operational_territories_mapper}
        
        ALPHANUMERIC_AND_SYMBOLS = ALPHANUMERIC +'@#$%=:?.,/|~>*()<'
        for clinician in full_roster:
            # email, name, and role are are required, skip if no email nor name
            if not any((clinician.get('email'), clinician.get('name'), roles_mapper.get(clinician.get('practitioner_type')))):
                continue

            affiliate_id = clinician.get('uuid')

            # skip if clinician already in modobio system
            if affiliate_id in wheel_physician_ids:
                continue

            # extract info for modobio user account
            user_info =  { 
                'email': clinician.get('email'),
                'firstname': clinician.get('name').split()[0],
                'lastname': ' '.join(clinician.get('name').split()[1:]),
                'biological_sex_male': (True if clinician.get('sex') == 'Male' else False),
                'is_staff': True,
                'is_client': False
            }


            role = roles_mapper.get(clinician.get('practitioner_type'))

            state_medical_license_details = clinician.get('license_info')

            ##
            # Create instances of User, StaffProfile, StaffRoles, StaffOperationalTerritories, 
            # TelehealthStaffSettings, PractitionerCredentials, UserProfilePictures
            ##
            user = User(**user_info)

            db.session.add(user)
            db.session.flush()

            user_login = UserLogin(user_id = user.user_id)
            tmp_password = "".join([random.choice(ALPHANUMERIC_AND_SYMBOLS) for i in range(12)])
            user_login.set_password(tmp_password)
            db.session.add(user_login)

            staff_profile = StaffProfile(user_id = user.user_id, bio = clinician.get('about') )
            db.session.add(staff_profile)

            staff_roles = StaffRoles(user_id = user.user_id, role = role, granter_id = user.user_id)
            db.session.add(staff_roles)
            db.session.flush()

            staff_operational_territories = [StaffOperationalTerritories(**{
                'user_id': user.user_id,
                'role_id': staff_roles.idx, 
                'operational_territory_id': operational_territories_mapper[state.lower()]}) for state in state_medical_license_details]
            db.session.add_all(staff_operational_territories)
            db.session.flush()

            practitioner_credentials = []
            if clinician.get('npi'):
                practitioner_credentials.append(PractitionerCredentials(**{
                    'user_id': user.user_id,
                    'role_id': staff_roles.idx,
                    'country_id': 1 ,
                    'status': 'Pending Verification',
                    'credential_type': 'NPI',
                    'credentials':clinician.get('npi'),
                    'want_to_practice': True}))

            for state, _license in state_medical_license_details.items():
                license_details = {
                    'user_id': user.user_id,
                    'role_id': staff_roles.idx,
                    'country_id': 1 ,
                    'state': state.upper(), 
                    'expiration_date': _license[0]['expires_at'],
                    'status': 'Pending Verification',
                    'credential_type': 'Medical License',
                    'credentials':_license[0]['license_number'],
                    'want_to_practice': True}
                practitioner_credentials.append(PractitionerCredentials(**license_details))
            
            db.session.add_all(practitioner_credentials)
            db.session.flush()

            telehealth_settings = TelehealthStaffSettings(
                user_id = user.user_id, 
                auto_confirm = False, 
                timezone = (clinician.get('timezone') if clinician.get('timezone') else 'UTC'))
            db.session.add(telehealth_settings)
            
            ###
            # Save profile pic
            ###

            #  if provided, get profile picture and store in s3
            # if profile_picture field was included, profile pic is removed
            # then if image was provided, it is updated, otherwise, it remains deleted
            fh = FileHandling()
            _prefix = f'id{user.user_id:05d}/staff_profile_picture'
            
            # when an image is provided, then the image is updated to the new one
            # we're only allowing one profile picture for staff profile, so only one will be processed
            response = requests.get(clinician.get('photo'), stream=True)
            
            if response:
                # validate file size - safe threashold (MAX = 10 mb)
                img = BytesIO(response.content)
                fh.validate_file_size(img, IMAGE_MAX_SIZE)
                # validate file type
                import imghdr
                
                img_extension = '.' + imghdr.what('', response.content)
                if img_extension not in ALLOWED_IMAGE_TYPES:
                    return

                tmp = Image.open(img)
                tfile = BytesIO()
                img_w, img_h = tmp.size
                tmp.save(tfile, format='jpeg')
                original_s3key = f'{_prefix}/original{img_extension}'
                img_file = FileStorage(tfile, filename=f'size{img_w}x{img_h}.jpeg', content_type=f'image/jpeg')

                fh.save_file_to_s3(img_file, original_s3key)
                # Save original to S3

                # Save original to db
                user_profile_pic = UserProfilePictures()
                user_profile_pic.original = True
                user_profile_pic.staff_id = user.user_id
                user_profile_pic.image_path = original_s3key
                user_profile_pic.width = img_w
                user_profile_pic.height = img_h
                db.session.add(user_profile_pic)

                # crop image to a square
                squared = fh.image_crop_square(img_file)

                # resize to sizes specified by the tuple of tuples in constant IMAGE_DEMENSIONS
                for dimension in IMAGE_DIMENSIONS:
                    _img = fh.image_resize(squared, dimension)
                    # save to s3 bucket
                    #add all 3 files to S3 - Naming it specifically as staff_profile_picture to differentiate from client profile pic
                    #format: id{user_id:05d}/staff_profile_picture/size{img.length}x{img.width}.img_extension)
                    _img_s3key = f'{_prefix}/{_img.filename}'
                    fh.save_file_to_s3(_img, _img_s3key)

                    # save to database
                    w, h = dimension
                    user_profile_pic = UserProfilePictures()
                    user_profile_pic.staff_id = user.user_id
                    user_profile_pic.image_path = _img_s3key
                    user_profile_pic.width = w
                    user_profile_pic.height = h
                    user_profile_pic.original = False
                    db.session.add(user_profile_pic)
                

            db.session.commit()

    def cancel_booking(self, external_booking_id: str):
        """
        Cancel the wheel consultation using PATCH v1/consults/<external_booking_id>/cancel

        Expected response is 200 OK and payload of {"status": "success"}
        """

        url = self.url_base+ f"/v1/consults/{external_booking_id}/cancel"

        response = requests.patch(
                url,
                headers={'x-api-key': self.wheel_api_token,
                'Content-Type': 'application/json'},
            )

        # user must attempt this request again later
        # TODO: Consider making this a recoverable situation by retrying
        try:
            response.raise_for_status()
        except Exception as e:
            raise GenericThirdPartyError(status_code = response.status_code, message=response.json())

        return

    def start_consult(self, external_booking_id: str):
        """
        Send a consult start request to wheel. 

        Params
        -------
        external_booking_id: 
            Booking reference id from TelehealthBookings.external_booking_id
        """

        url = self.url_base+ f"/v1/consults/{external_booking_id}/start"

        response = requests.patch(
                url,
                headers={'x-api-key': self.wheel_api_token,
                'Content-Type': 'application/json'},
            )

        # user must attempt this request again later
        # TODO: Consider making this a recoverable situation by retrying
        try:
            response.raise_for_status()
        except Exception as e:
            raise GenericThirdPartyError(status_code = response.status_code, message=response.json())

        return

    def complete_consult(self, external_booking_id: str):
        """
        Send a consult complete request to wheel. 

        Params
        -------
        external_booking_id: 
            Booking reference id from TelehealthBookings.external_booking_id
        """

        url = self.url_base+ f"/v1/consults/{external_booking_id}/complete"

        response = requests.patch(
                url,
                headers={'x-api-key': self.wheel_api_token,
                'Content-Type': 'application/json'},
            )

        # user must attempt this request again later
        # TODO: Consider making this a recoverable situation by retrying
        try:
            response.raise_for_status()
        except Exception as e:
            raise GenericThirdPartyError(status_code = response.status_code, message=response.json())

        return
