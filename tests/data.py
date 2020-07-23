import base64
import datetime
import pathlib
import uuid

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
    "dob": "1991-10-14",
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
    "dob": "1991-10-14",
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

test_client_consent_data = {
    'infectious_disease': False,
    'signdate': "2020-04-05",
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.consent]
}

test_client_release_data = {
    'release_by_other': 'My wife can also release my data.',
    'release_of_all': False,
    'release_of_other': 'Only release my prescription drugs, not anything else.',
    'release_date_from': "2020-07-07",
    'release_date_to': "2021-07-07",
    'release_purpose': 'Release my data for the purpose of doctors having my required drugs.',
    'signdate': "2020-05-05",
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.release]
}

test_client_policies_data = {
    'signdate': "2020-04-05",
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.policies]
}

test_client_consult_data = {
    'signdate': "2020-04-05",
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.consult]
}

test_client_subscription_data = {
    'signdate': "2020-04-05",
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.subscription]
}

test_client_individual_data = {
    'doctor': True,
    'pt': True,
    'data': False,
    'drinks': True,
    'signdate': "2020-04-05",
    'signature': signature,
    'revision': DOCTYPE_DOCREV_MAP[DOCTYPE.individual]
}

test_json_data = {
    'a': 1,
    'b': 1.1,
    'c': True,
    'd': 'string',
    'e': {
        'aa': 11,
        'bb': 'bigger string'
    },
    'f': [1, 2, 3, 4, 5],
    'g': "1977-04-05",
    'h': datetime.time(14, 21, 39, 123456).isoformat(),
    'i': datetime.datetime(2020, 6, 7, 12, 39, 46, 123456).isoformat(),
    'j': {
        'ja': {
            'jja': [datetime.time(13, 0, 0).isoformat(), datetime.time(14, 0, 0).isoformat(), datetime.time(15, 0, 0).isoformat()],
        }
    },
    'k': '17a3bee0-42db-4416-8b84-3990b1c6397e',
}

test_json_json = '{"a": 1, "b": 1.1, "c": true, "d": "string", "e": {"aa": 11, "bb": "bigger string"}, "f": [1, 2, 3, 4, 5], "g": "1977-04-05", "h": "14:21:39.123456", "i": "2020-06-07T12:39:46.123456", "j": {"ja": {"jja": ["13:00:00", "14:00:00", "15:00:00"]}}, "k": "17a3bee0-42db-4416-8b84-3990b1c6397e"}'

# This will be run in test, so JSONIFY_PRETTYPRINT_REGULAR is True by default.
# It affects spaces and indentation in jsonify output.
test_json_jsonify = b'{\n  "a": 1, \n  "b": 1.1, \n  "c": true, \n  "d": "string", \n  "e": {\n    "aa": 11, \n    "bb": "bigger string"\n  }, \n  "f": [\n    1, \n    2, \n    3, \n    4, \n    5\n  ], \n  "g": "1977-04-05", \n  "h": "14:21:39.123456", \n  "i": "2020-06-07T12:39:46.123456", \n  "j": {\n    "ja": {\n      "jja": [\n        "13:00:00", \n        "14:00:00", \n        "15:00:00"\n      ]\n    }\n  }, \n  "k": "17a3bee0-42db-4416-8b84-3990b1c6397e"\n}\n'
