import pathlib

doctor_personalfamilyhist_post_data = {
  "conditions":[
    {
      "medical_condition_id": 1,
      "myself": True,
      "father": True,
      "mother": True,
      "sister": True,
      "brother": True
    },
    {
      "medical_condition_id": 2,
      "myself": False,
      "father": False,
      "mother": False,
      "sister": False,
      "brother": False
    }    
  ]
}

doctor_personalfamilyhist_put_data = {
  "conditions":[
    {
      "medical_condition_id": 1,
      "myself": False,
      "father": False,
      "mother": False,
      "sister": False,
      "brother": False
    }  
  ]
}

doctor_clients_external_medical_records_data = {
  "record_locators": [
    {
        "med_record_id": "sadfgg65",
        "institute_id": 9999,
        "institute_name": "Regular Doc Two"
    },
    {
        "med_record_id": "sadfgdrg65",
        "institute_id": 2,
        "institute_name": ""
    },
    {
        "med_record_id": "sad65",
        "institute_id": 1,
        "institute_name": ""
    }
  ]
}

doctor_medical_history_data = {
  "allergies": "new allergy",
  "concerns": "no real concerns",
  "diagnostic_other": "string",
  "diagnostic_ultrasound": "string",
  "diagnostic_endoscopy": "string",
  "family_history": "string",
  "social_history": "string",
  "diagnostic_mri": "string",
  "diagnostic_xray": "string",
  "last_examination_date": "2020-07-30",
  "diagnostic_ctscan": "string",
  "goals": "string",
  "last_examination_reason": "string",
  "medication": "string"
}

doctor_blood_tests_data = {
    "date": "2020-09-10",
    "results": [
        {"result_name": "cholesterolSerumTotal","result_value": 150.0},
        {"result_name": "cholesterolSerumLDL", "result_value": 20.0}
    ],
    "panel_type": "Lipids",
    "notes": "test2"
}

img_file = pathlib.Path(__file__).parent / 'test_jpg_image.jpg'
doctor_medical_imaging_data = {
  'image': (img_file.as_posix() , open(img_file, mode='rb'), 'image/jpg'),
  'image_date': '2020-09-29',
  'image_origin_location': 'testing clinic',
  'image_type': 'X-ray',
  'image_read': 'Check Check'
}

