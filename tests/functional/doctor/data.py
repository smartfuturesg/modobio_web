import pathlib

doctor_blood_pressures_data = {
  'systolic': 120.2,
  'diastolic': 52.3,
  'datetime_taken': '2020-04-05T02:00:00.000'
}

doctor_all_generalmedicalinfo_post_5_data = {
    'allergies': [{
        'allergy_symptoms': 'Rash'
    }
    ]
}

doctor_all_generalmedicalinfo_post_4_data = {
  'gen_info': {
      'primary_doctor_contact_name': 'Dr Dude',
      'primary_doctor_contact_phone': '4809999999',
      'primary_doctor_contact_email': 'drguy@gmail.com',
      'blood_type': 'A',
      'blood_type_positive': True
  },
    'allergies': [{
        'medication_name': 'medName3',
        'allergy_symptoms': 'Rash'
    }
    ]
}

doctor_all_socialhistory_break_post_2_data = {
  'social_history': {
    'ever_smoked': True,
    'currently_smoke': False,
    'last_smoke': 5,
    'last_smoke_time': 'months',
    'avg_weekly_drinks': 1,
    'avg_weekly_workouts': 2,
    'job_title': 'Engineer',
    'avg_hourly_meditation': 3,
    'sexual_preference': 'Female'
  },
  'std_history': [
    {
      'std_id': 7
    },
    {
      'std_id': 25
    }
  ]
}

doctor_all_socialhistory_break_post_1_data = {
  'social_history': {
    'ever_smoked': True,
    'currently_smoke': False,
    'last_smoke_time': 'months',
    'avg_weekly_drinks': 1,
    'avg_weekly_workouts': 2,
    'job_title': 'Engineer',
    'avg_hourly_meditation': 3,
    'sexual_preference': 'Female'
  },
  'std_history': [
    {
      'std_id': 7
    }
  ]
}
# This is the payload that the frontend was sending
# that was causing the error
doctor_all_socialhistory_post_3_data = {
  'social_history': {
    'currently_smoke': False,
    'last_smoke': 1,
    'last_smoke_time': '',
    'avg_weekly_drinks': 0,
    'avg_weekly_workouts': 0,
    'job_title': '',
    'avg_hourly_meditation': 0,
    'sexual_preference': '',
    'plan_to_stop': None,
    'num_years_smoked': 0,
    'avg_num_cigs': 0
  },
  'std_history': []
}

doctor_all_socialhistory_post_2_data = {
  'social_history': {
    'ever_smoked': True,
    'currently_smoke': False,
    'last_smoke': 5,
    'last_smoke_time': 'months',
    'avg_weekly_drinks': 1,
    'avg_weekly_workouts': 2,
    'job_title': 'Engineer',
    'avg_hourly_meditation': 3,
    'sexual_preference': 'Female'
  },
  'std_history': [
    {
      'std_id': 7
    }
  ]
}

doctor_all_socialhistory_post_1_data = {
  'social_history': {
    'ever_smoked': True,
    'currently_smoke': True,
    'avg_num_cigs': 5,
    'num_years_smoked': 6,
    'plan_to_stop': False,
    'avg_weekly_drinks': 1,
    'avg_weekly_workouts': 2,
    'job_title': 'Engineer',
    'avg_hourly_meditation': 3,
    'sexual_preference': 'Female'
  },
  'std_history': [
    {
      'std_id': 1
    },
    {
      'std_id': 2
    },
    {
      'std_id': 5
    }
  ]
}

doctor_all_generalmedicalinfo_post_3_data = {
  'gen_info': {
      'primary_doctor_contact_name': 'Dr Dude',
      'primary_doctor_contact_phone': '4809999999',
      'primary_doctor_contact_email': 'drguy@gmail.com',
      'blood_type': 'A',
      'blood_type_positive': True
  },
  'medications': [{
        'medication_dosage': 1.2,
        'medication_units': 'mg',
        'medication_freq': 4,
        'medication_times_per_freq': 3,
        'medication_time_units': 'day'
    },
    {
        'medication_name': 'medName2',
        'medication_dosage': 3,
        'medication_units': 'mg',
        'medication_freq': 5,
        'medication_times_per_freq': 6,
        'medication_time_units': 'day'
    },
    {
        'medication_name': 'medName5',
        'medication_dosage': 7,
        'medication_units': 'mg',
        'medication_freq': 5,
        'medication_times_per_freq': 6,
        'medication_time_units': 'day'
    }
    ],
    'allergies': [{
        'medication_name': 'medName3',
        'allergy_symptoms': 'Rash'
    }
    ]
}

doctor_all_generalmedicalinfo_post_2_data = {
  'gen_info': {
      'primary_doctor_contact_name': 'Dr Steve',
      'primary_doctor_contact_phone': '4809999999',
      'primary_doctor_contact_email': 'drguy@gmail.com',
      'blood_type': 'A',
      'blood_type_positive': True
  },
  'medications': [{
        'medication_name': 'medName4',
        'medication_dosage': 1.2,
        'medication_units': 'mg',
        'medication_freq': 4,
        'medication_times_per_freq': 3,
        'medication_time_units': 'day'
    },
    {
        'medication_name': 'medName2',
        'medication_dosage': 3,
        'medication_units': 'mg',
        'medication_freq': 5,
        'medication_times_per_freq': 6,
        'medication_time_units': 'day'
    },
    {
        'medication_name': 'medName5',
        'medication_dosage': 7,
        'medication_units': 'mg',
        'medication_freq': 5,
        'medication_times_per_freq': 6,
        'medication_time_units': 'day'
    }
    ],
    'allergies': [{
        'medication_name': 'medName3',
        'allergy_symptoms': 'Rash'
    }
    ]
}

doctor_all_generalmedicalinfo_post_1_data = {
  'gen_info': {
      'primary_doctor_contact_name': 'Dr Guy',
      'primary_doctor_contact_phone': '4809999999',
      'primary_doctor_contact_email': 'drguy@gmail.com',
      'blood_type': 'A',
      'blood_type_positive': True
  },
  'medications': [{
        'medication_name': 'medName4',
        'medication_dosage': 1.2,
        'medication_units': 'mg',
        'medication_freq': 4,
        'medication_times_per_freq': 3,
        'medication_time_units': 'day'
    },
    {
        'medication_name': 'medName2',
        'medication_dosage': 3,
        'medication_units': 'mg',
        'medication_freq': 5,
        'medication_times_per_freq': 6,
        'medication_time_units': 'day'
    }
    ],
    'allergies': [{
        'medication_name': 'medName3',
        'allergy_symptoms': 'Rash'
    },
    {
        'medication_name': 'medName3',
        'allergy_symptoms': 'Vertigo'
    },
    {
        'medication_name': 'medName1',
        'allergy_symptoms': 'Vertigo'
    }
    ]
}

doctor_std_delete_data = {
  'stds':[
    {
      'std_id': 2
    }
  ]
}

doctor_std_post_1_data = {
  'stds':[
    {
      'std_id': 1
    },
    {
      'std_id': 2
    }
  ]
}

doctor_socialhist_put_data = {
  'currently_smoke': True,
  'avg_num_cigs': 5,
  'num_years_smoked': 6,
  'plan_to_stop': False,
  'avg_weekly_drinks': 1,
  'avg_weekly_workouts': 2,
  'job_title': 'Engineer',
  'avg_hourly_meditation': 3,
  'sexual_preference': 'Female'
}

doctor_socialhist_post_data = {
  'currently_smoke': False,
  'last_smoke': 5,
  'last_smoke_time': 'months',
  'avg_weekly_drinks': 1,
  'avg_weekly_workouts': 2,
  'job_title': 'Engineer',
  'avg_hourly_meditation': 3,
  'sexual_preference': 'Female'
}

doctor_medicalgeneralinfo_put_data = {
      'primary_doctor_contact_name': 'Dr Steve',
      'primary_doctor_contact_phone': '4809999999',
      'primary_doctor_contact_email': 'drguy@gmail.com',
      'blood_type': 'A',
      'blood_type_positive': True
}

doctor_medicalmedicationsinfo_delete_data = {
  'delete_ids':[
    {'idx': 2}
  ]
}

doctor_medicalmedicationsinfo_put_data = {
    'medications': [{
        'idx': 1,
        'medication_name': 'medName4',
        'medication_dosage': 1.2,
        'medication_units': 'mg',
        'medication_freq': 4,
        'medication_times_per_freq': 3,
        'medication_time_units': 'day'
    },
    {
        'idx': 2,
        'medication_name': 'medName2',
        'medication_dosage': 3,
        'medication_units': 'mg',
        'medication_freq': 5,
        'medication_times_per_freq': 6,
        'medication_time_units': 'day'
    }
    ]
}

doctor_medicalallergiesinfo_delete_data = {
  'delete_ids':[
    {'idx': 2}
  ]
}

doctor_medicalallergiesinfo_put_data = {
    'allergies': [{
        'idx': 1,
        'medication_name': 'medName4',
        'allergy_symptoms': 'Rash'
    }
    ]
}

doctor_medicalgeneralinfo_post_data = {
      'primary_doctor_contact_name': 'Dr Guy',
      'primary_doctor_contact_phone': '4809999999',
      'primary_doctor_contact_email': 'drguy@gmail.com',
      'blood_type': 'A',
      'blood_type_positive': True
}

doctor_medicalmedicationsinfo_post_data = {
    'medications': [{
        'medication_name': 'medName1',
        'medication_dosage': 1.2,
        'medication_units': 'mg',
        'medication_freq': 4,
        'medication_times_per_freq': 3,
        'medication_time_units': 'day'
    },
    {
        'medication_name': 'medName2',
        'medication_dosage': 2.1,
        'medication_units': 'mg',
        'medication_freq': 5,
        'medication_times_per_freq': 6,
        'medication_time_units': 'day'
    }
    ]
}

doctor_medicalallergiesinfo_post_data = {
    'allergies': [{
        'medication_name': 'medName3',
        'allergy_symptoms': 'Rash'
    },
    {
        'medication_name': 'medName3',
        'allergy_symptoms': 'Vertigo'
    },
    {
        'medication_name': 'medName1',
        'allergy_symptoms': 'Vertigo'
    }
    ]
}

doctor_personalfamilyhist_post_data = {
  'conditions':[
    {
      'medical_condition_id': 1,
      'myself': True,
      'father': True,
      'mother': True,
      'sister': True,
      'brother': True
    },
    {
      'medical_condition_id': 2,
      'myself': True,
      'father': False,
      'mother': False,
      'sister': False,
      'brother': False
    }
  ]
}

doctor_personalfamilyhist_put_data = {
  'conditions':[
    {
      'medical_condition_id': 1,
      'myself': True,
      'father': False,
      'mother': False,
      'sister': False,
      'brother': False
    },
    {
      'medical_condition_id': 2,
      'myself': False,
      'father': False,
      'mother': False,
      'sister': False,
      'brother': False
    },
    {
      'medical_condition_id': 3,
      'myself': False,
      'father': True,
      'mother': False,
      'sister': False,
      'brother': False
    }
  ]
}

doctor_clients_external_medical_records_data = {
  'record_locators': [
    {
        'med_record_id': 'sadfgg65',
        'institute_id': 9999,
        'institute_name': 'Regular Doc Two'
    },
    {
        'med_record_id': 'sadfgdrg65',
        'institute_id': 2,
        'institute_name': ''
    },
    {
        'med_record_id': 'sad65',
        'institute_id': 1,
        'institute_name': ''
    }
  ]
}

doctor_medical_history_data = {
  'allergies': 'new allergy',
  'concerns': 'no real concerns',
  'diagnostic_other': 'string',
  'diagnostic_ultrasound': 'string',
  'diagnostic_endoscopy': 'string',
  'family_history': 'string',
  'social_history': 'string',
  'diagnostic_mri': 'string',
  'diagnostic_xray': 'string',
  'last_examination_date': '2020-07-30',
  'diagnostic_ctscan': 'string',
  'goals': 'Gut Health',
  'last_examination_reason': 'string',
  'medication': 'string'
}

doctor_blood_tests_data = {
    'date': '2021-09-10',
    'results': [
        {'modobio_test_code': 'CMP001','result_value': 301.0},
        {'modobio_test_code': 'CMP002', 'result_value': 40.0},
        {'modobio_test_code': 'CMP010','result_value': 10.0},
        {'modobio_test_code': 'HOR003','result_value': 1.0},
        {'modobio_test_code': 'TST003','result_value': 0.2}
    ],
    'notes': 'test2'
}

img_file = pathlib.Path(__file__).parent / 'test_pdf_image.pdf'

doctor_blood_tests_image_data = {
  'image': (img_file.open(mode='rb'), img_file.as_posix())
}

img_file = pathlib.Path(__file__).parent / 'test_jpg_image.jpg'

doctor_medical_imaging_data = {
  'image': (img_file.open(mode='rb'), img_file.as_posix()),
  'image_date': '2020-09-29',
  'image_origin_location': 'testing clinic',
  'image_type': 'X-ray',
  'image_read': 'Check Check'
}

doctor_surgery_data = {
  'surgery_category': 'Heart',
  'date': '2020-11-23',
  'notes': 'test some notes',
  'surgeon': 'John Q. Surgeon',
  'institution': 'Our Lady of Perpetual Surgery',
}

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