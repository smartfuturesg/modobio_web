import pathlib

doctor_medicalgeneralinfo_put_data = {
      "primary_doctor_contact_name": "Dr Steve",
      "primary_doctor_contact_phone": "4809999999",
      "primary_doctor_contact_email": "drguy@gmail.com",
      "blood_type": "A",
      "blood_type_positive": True
}

doctor_medicalmedicationsinfo_put_data = {
    "medications": [{
        "medication_name": "medName4",
        "medication_dosage": 1.2,
        "medication_units": "mg",
        "medication_freq": 4,
        "medication_times_per_freq": 3,
        "medication_time_units": "day"
    },
    {
        "medication_name": "medName2",
        "medication_dosage": 3,
        "medication_units": "mg",
        "medication_freq": 5,
        "medication_times_per_freq": 6,
        "medication_time_units": "day"
    } 
    ]
}

doctor_medicalallergiesinfo_put_data = {
    "allergies": [{
        "medication_name": "medName3",
        "allergy_symptoms": "Rash"
    },
    {                                   
        "medication_name": "medName4",
        "allergy_symptoms": "Rash"
    },   
    ]
}

doctor_medicalgeneralinfo_post_data = {
      "primary_doctor_contact_name": "Dr Guy",
      "primary_doctor_contact_phone": "4809999999",
      "primary_doctor_contact_email": "drguy@gmail.com",
      "blood_type": "A",
      "blood_type_positive": True
}

doctor_medicalmedicationsinfo_post_data = {
    "medications": [{
        "medication_name": "medName1",
        "medication_dosage": 1.2,
        "medication_units": "mg",
        "medication_freq": 4,
        "medication_times_per_freq": 3,
        "medication_time_units": "day"
    },
    {
        "medication_name": "medName2",
        "medication_dosage": 2.1,
        "medication_units": "mg",
        "medication_freq": 5,
        "medication_times_per_freq": 6,
        "medication_time_units": "day"
    } 
    ]
}

doctor_medicalallergiesinfo_post_data = {
    "allergies": [{
        "medication_name": "medName3",
        "allergy_symptoms": "Rash"
    },
    {                                   
        "medication_name": "medName3",
        "allergy_symptoms": "Vertigo"
    }    
    ]
}

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
    },
    {
      "medical_condition_id": 3,
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
  "goals": "Gut Health",
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

doctor_surgery_data = {
  "surgery_category": "Heart",
  "date": "2020-11-23",
  "notes": "test some notes",
  "surgeon": "John Q. Surgeon",
  "institution": "Our Lady of Perpetual Surgery",
}