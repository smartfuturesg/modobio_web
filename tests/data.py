import base64
import datetime
import pathlib

from odyssey.constants import DOCTYPE, DOCTYPE_DOCREV_MAP

test_client_info = {
    "firstname": "Test",
    "middlename": "This",
    "lastname": "Client",
    "guardianname": "guardian 1",
    "guardianrole": "guardian role",
    "street": "3325 S Malibu Dr.",
    "city": "Tempe",
    "state": "AZ",
    "zipcode": "85282",
    "country": "US",
    "email": "test_this_client@gmail.com",
    "phone": "4805555555",
    "preferred": 0,
    "ringsize": 11,
    "emergency_contact": "Emergency",
    "emergency_phone": "6025555555",
    "healthcare_contact": "United",
    "healthcare_phone": "1800676blue",
    "gender": "m",
    #"dob": "1991-10-14",
    "profession": "Chef",
    "receive_docs": True
}

test_new_remote_registration = {
    "firstname": "Remote",
    "middlename": "Client",
    "lastname": "Test",
    "email": "rest_remote_registration@gmail.com"
    }

test_new_client_info = {
    "firstname": "Test",
    "middlename": "This",
    "lastname": "Client Two",
    "guardianname": "guardian 1",
    "guardianrole": "guardian role",
    "street": "3325 S Malibu Dr.",
    "city": "Tempe",
    "state": "AZ",
    "zipcode": "85282",
    "country": "US",
    "email": "test_this_client_two@gmail.com",
    "phone": "4805555555",
    "preferred": 0,
    "ringsize": 11,
    "emergency_contact": "Emergency",
    "emergency_phone": "6025555555",
    "healthcare_contact": "United",
    "healthcare_phone": "1800676blue",
    "gender": "m",
    #"dob": "1991-10-14",
    "profession": "Chef",
    "receive_docs": True
}

test_staff_member = {
    "firstname": "testy",
    "lastname": "testerson",
    "email": "staff_member@modobio.com",
    "password": "password",
    "is_admin": True,
    "is_system_admin": False,
    "access_role": "data"
}

signature = None
signature_file = pathlib.Path(__file__).parent / 'signature.png'
with open(signature_file, mode='rb') as fh:
    signature = fh.read()

signature = 'data:image/png;base64,' + base64.b64encode(signature).decode('utf-8')

test_client_consent_form = {
    'infectious_disease': False,
    'signdate': datetime.date(2020, 4, 5),
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.consent]
}

test_client_release_form = {
    'release_by_other': 'My wife can also release my data.',
    'release_of_all': False,
    'release_of_other': 'Only release my prescription drugs, not anything else.',
    'release_date_from': datetime.date(2020, 7, 7),
    'release_date_to': datetime.date(2021, 7, 7),
    'release_purpose': 'Release my data for the purpose of doctors having my required drugs.',
    'signdate': datetime.date(2020, 4, 5),
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.release]
}

test_client_policies_form = {
    'signdate': datetime.date(2020, 4, 5),
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.policies]
}

test_client_consult_contract = {
    'signdate': datetime.date(2020, 4, 5),
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.consult]
}

test_client_subscription_contract = {
    'signdate': datetime.date(2020, 4, 5),
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.subscription]
}

test_client_individual_contract = {
    'doctor': True,
    'pt': True,
    'data': False,
    'drinks': True,
    'signdate': datetime.date(2020, 4, 5),
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.individual]
}
