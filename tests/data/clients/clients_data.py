import base64
import pathlib

# clients_info_data = {
#     "firstname": "Test",
#     "middlename": "This",
#     "lastname": "Client",
#     "guardianname": "guardian 1",
#     "guardianrole": "guardian role",
#     "street": "3325 S Malibu Dr.",
#     "city": "Tempe",
#     "state": "AZ",
#     "zipcode": "85282",
#     "country": "US",
#     "email": "test_this_client@gmail.com",
#     "phone": "4805555555",
#     "preferred": 0,
#     "ringsize": 11,
#     "emergency_contact": "Emergency",
#     "emergency_phone": "6025555555",
#     "healthcare_contact": "United",
#     "healthcare_phone": "1800676blue",
#     "gender": "m",
#     "dob": "1991-10-14",
#     "profession": "Chef",
#     "receive_docs": True
# }
# clients_new_user_client_2_data = {
#   "userinfo": {
#     "firstname": "Test",
#     "middlename": "User",
#     "lastname": "Client",
#     "email": "test_this_user_client_2@modobio.com",
#     "phone_number": "1111111111",
#     "password": "password",
#     "is_staff": False,
#     "is_client": True
#   },
#   "clientinfo": {
#     "guardianname": "guardian 1",
#     "guardianrole": "guardian role",
#     "street": "3325 S Malibu Dr.",
#     "city": "Tempe",
#     "state": "AZ",
#     "zipcode": "85282",
#     "country": "US",
#     "preferred": 0,
#     "emergency_contact": "Emergency",
#     "emergency_phone": "6025555555",
#     "healthcare_contact": "United",
#     "healthcare_phone": "1800676blue",
#     "gender": "m",
#     "dob": "1991-10-14",
#     "profession": "Chef",
#     "receive_docs": True
#   }
# }

# clients_new_remote_registration_data = {
#     "firstname": "Remote",
#     "middlename": "Client",
#     "lastname": "Test",
#     "email": "rest_remote_registration@gmail.com"
# }

signature = None
signature_file = pathlib.Path(__file__).parent / 'signature.png'
with open(signature_file, mode='rb') as fh:
    signature = fh.read()

signature = 'data:image/png;base64,' + base64.b64encode(signature).decode('utf-8')

clients_consent_data = {
    'infectious_disease': False,
    'signdate': "2020-04-05",
    'signature': signature
}

# clients_release_data = {
#     'release_of_other': 'Only release my prescription drugs, not anything else.',
#     'release_date_from': "2020-07-07",
#     'release_date_to': "2021-07-07",
#     'release_purpose': 'Release my data for the purpose of doctors having my required drugs.',
#     'signdate': "2020-05-05",
#     'signature': signature,
#     "release_from": [{
#             "email": "string@gmail.com",
#             "release_direction": "FROM",
#             "name": "string",
#             "phone": "string",
#             "relationship": "string"
#             },
#             {
#             "email": "string@gmail.com",
#             "release_direction": "FROM",
#             "name": "string",
#             "phone": "string",
#             "relationship": "string"
#             }
#     ],
#   "release_to": [{
#             "email": "string@gmail.com",
#             "release_direction": "TO",
#             "name": "string",
#             "phone": "string",
#             "relationship": "string"
#             },
#             {
#             "email": "string@gmail.com",
#             "release_direction": "TO",
#             "name": "string",
#             "phone": "string",
#             "relationship": "string"
#             }
#   ],
#     "release_of_all": False,
# }

clients_policies_data = {
    'signdate': "2020-04-05",
    'signature': signature
}

clients_consult_data = {
    'signdate': "2020-04-05",
    'signature': signature
}

clients_subscription_data = {
    'signdate': "2020-04-05",
    'signature': signature
}

# clients_individual_data = {
#     'doctor': True,
#     'pt': True,
#     'data': False,
#     'drinks': True,
#     'signdate': "2020-04-05",
#     'signature': signature
# }