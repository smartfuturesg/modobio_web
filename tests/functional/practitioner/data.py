pracitioner_affiliation_data = {
    'organization_1': {
        'organization_idx': 1,
        'affiliate_user_id': '123'
    },
    'organization_2': {
        'organization_idx': 2,
        'affiliate_user_id': '123'
    },
    'invalid_organization_idx': {
        'organization_idx': 50,
        'affiliate_user_id': '123'
    }
}

pracitioner_consultation_rate_data = {
    'items': [
        {'role': 'medical_doctor','rate': '100.00'}
        ]
}


practitioner_credentials_post_1_data = {
  'items': [
    {'credential_type':'npi', 'country_id':1,'credentials': '1296336567', 'staff_role':'medical_doctor'},
    {'credential_type':'dea', 'country_id':1,'state': 'FL','credentials': '183451435', 'staff_role':'therapist'}, 
    {'credential_type':'dea', 'country_id':1,'state': 'CA','credentials': '123342534', 'staff_role':'medical_doctor'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'FL','credentials': '523746512', 'staff_role':'therapist'}, 
    {'credential_type':'med_lic', 'country_id':1,'state': 'CA','credentials': '839547692', 'staff_role':'medical_doctor'}
  ]
}


practitioner_credentials_post_2_data = {
  'items': [
    {'credential_type':'npi', 'country_id':1,'state': 'CA','credentials': '98714234', 'staff_role':'dietitian'},
    {'credential_type':'npi', 'country_id':1,'state': 'CA','credentials': '43218470', 'staff_role':'medical_doctor'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'FL','credentials': '21323512', 'staff_role':'therapist'}, 
  ]
}

practitioner_credentials_post_3_data = {
  'items': [
    {'credential_type':'npi', 'country_id':1,'state': 'CA','credentials': '98714234', 'staff_role':'medical_doctor'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'CA','credentials': '43218470', 'staff_role':'therapist'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'FL', 'staff_role':'dietitian'}, 
  ]
}

practitioner_credentials_put_1_data = {
    "idx": None, #idx will be set in test
    "state": "AZ",
    "country_id": 1,
    "credential_type": "npi"
}

practitioner_credentials_put_2_data = {
    "idx": None, #idx will be set in test
    "state": "TX",
    "country_id": 1,
    "credential_type": "npi"
}

practitioner_credentials_delete_1_data = {
    'idx': None #idx will be set in test
}