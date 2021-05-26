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

client_info_put_test_data = {
    "user_info": {
        "phone_number": "1111111111",
        "biological_sex_male": True,
        "firstname": "Tester",
        "middlename": "Name",
        "lastname": "Tested",
    },
    "client_info": {
        "dob": "1991-10-14",
        "zipcode": "85282",
        "city": "Tempe",
        "receive_docs": True,
        "primary_pharmacy_name": "Maw and Paw Drugs Co.",
        "healthcare_contact": "United",
        "primary_goal_id": 1,
        "country": "US",
        "emergency_contact": "Emergency",
        "state": "AZ",
        "street": "3325 S Malibu Dr.",
        "gender": "m",
        "guardianrole": "guardian role",
        "emergency_phone": "6025555555",
        "primary_pharmacy_address": "9550 E Main St, Mesa, AZ 85207",
        "guardianname": "guardian 1",
        "healthcare_phone": "1800676blue",
        "preferred": 0,
        "profession": "Chef"
    }
}

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

clients_release_data = {
    'release_of_other': 'Only release my prescription drugs, not anything else.',
    'release_date_from': "2020-07-07",
    'release_date_to': "2021-07-07",
    'release_purpose': 'Release my data for the purpose of doctors having my required drugs.',
    'signdate': "2020-05-05",
    'signature': signature,
    "release_from": [{
            "email": "string@gmail.com",
            "release_direction": "FROM",
            "name": "string",
            "phone": "string",
            "relationship": "string"
            },
            {
            "email": "string@gmail.com",
            "release_direction": "FROM",
            "name": "string",
            "phone": "string",
            "relationship": "string"
            }
    ],
  "release_to": [{
            "email": "string@gmail.com",
            "release_direction": "TO",
            "name": "string",
            "phone": "string",
            "relationship": "string"
            },
            {
            "email": "string@gmail.com",
            "release_direction": "TO",
            "name": "string",
            "phone": "string",
            "relationship": "string"
            }
  ],
    "release_of_all": False,
}

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

clients_individual_data = {
    'doctor': True,
    'pt': True,
    'data': False,
    'drinks': True,
    'signdate': "2020-04-05",
    'signature': signature
}

clients_clinical_care_team = {
    "care_team" : [
        {
            "team_member_email": "test_client@modomodo.com"
        },
        {
            "team_member_email": "test_client_two@modomodo.com"
        },
    ]
    
    }

clients_assigned_drinks = {
    "drink_id": 1
}

clients_mobile_settings = {
    "general_settings": {
        "is_right_handed": True,
        "enable_push_notifications": True,
        "display_middle_name": True,
        "biometrics_setup": True,
        "timezone_tracking": True,
        "use_24_hour_clock": True,
        "date_format": "%d-%b-%Y",
        "include_timezone": True
    },
    "push_notification_type_ids": [
        {"notification_type_id": 3},
        {"notification_type_id": 16},
        {"notification_type_id": 11}
  ]
}

clients_transactions = [
    {
        "category": "Telehealth",
        "payment_method": "Visa 0123",
        "name": "Doctor call",
        "price": 49.99,
        "currency": "USD"
    },
    {
        "category": "Telehealth",
        "payment_method": "Visa 0123",
        "name": "Diagnosis",
        "price": 89.99,
        "currency": "USD"
    }
]

clients_race_and_ethnicities = {
    'normal data':
    {
        'mother': [2,3,4],
        'father': [3,5]
    },
    'invalid race_id':
    {
        'mother': [2,4],
        'father': [999]
    },
    'unknown':
    {
        'mother': [],
        'father': [6,7]
    },
    'invalid combination':
    {
        'mother': [1,2],
        'father': [7,8,9,10]
    },
    'all ids':
    {
        'mother': [2,3,4,5,6,7,8,9,10,11,12],
        'father': [2,3,4,5,6,7,8,9,10,11,12]
    },
    'duplicates':
    {
        'mother': [1,1,1,1,1],
        'father': [2,2,2,4,6]
    },
    'non-numeric':
    {
        'mother': [9,10],
        'father': ['White, Caucasian']
    }
}