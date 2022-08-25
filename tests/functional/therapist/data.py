doctor_credentials_post_1_data = {
  'items': [
    {'credential_type':'npi', 'country_id':1,'credentials': '1296336567'},
    {'credential_type':'dea', 'country_id':1,'state': 'FL','credentials': '183451435'}, 
    {'credential_type':'dea', 'country_id':1,'state': 'CA','credentials': '123342534'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'FL','credentials': '523746512'}, 
    {'credential_type':'med_lic', 'country_id':1,'state': 'CA','credentials': '839547692'}
  ]
}


doctor_credentials_post_2_data = {
  'items': [
    {'credential_type':'npi', 'country_id':1,'state': 'CA','credentials': '98714234'},
    {'credential_type':'npi', 'country_id':1,'state': 'CA','credentials': '43218470'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'FL','credentials': '21323512'}, 
  ]
}

doctor_credentials_post_3_data = {
  'items': [
    {'credential_type':'npi', 'country_id':1,'state': 'CA','credentials': '98714234'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'CA','credentials': '43218470'},
    {'credential_type':'med_lic', 'country_id':1,'state': 'FL'}, 
  ]
}

doctor_credentials_put_1_data = {
    "idx": None, #idx will be set in test
    "want_to_practice": True,
    "state": "AZ",
    "country_id": 1,
    "credential_type": "npi"
}

doctor_credentials_put_2_data = {
    "idx": None, #idx will be set in test
    "want_to_practice": True,
    "state": "TX",
    "country_id": 1,
    "credential_type": "npi"
}

doctor_credentials_delete_1_data = {
    'idx': None #idx will be set in test
}