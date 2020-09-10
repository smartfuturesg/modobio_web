import base64
import datetime
import pathlib
import uuid

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

test_client_external_medical_records = {
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
    "access_roles": ["datasci"]
}

test_new_staff_member = {
    "firstname": "testy",
    "lastname": "testerson",
    "email": "staff_member_2@modobio.com",
    "password": "password",
    "access_roles": ["datasci"]
}

signature = None
signature_file = pathlib.Path(__file__).parent / 'signature.png'
with open(signature_file, mode='rb') as fh:
    signature = fh.read()

signature = 'data:image/png;base64,' + base64.b64encode(signature).decode('utf-8')

test_client_consent_data = {
    'infectious_disease': False,
    'signdate': "2020-04-05",
    'signature': signature
}

test_client_release_data = {
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

test_client_policies_data = {
    'signdate': "2020-04-05",
    'signature': signature
}

test_client_consult_data = {
    'signdate': "2020-04-05",
    'signature': signature
}

test_client_subscription_data = {
    'signdate': "2020-04-05",
    'signature': signature
}

test_client_individual_data = {
    'doctor': True,
    'pt': True,
    'data': False,
    'drinks': True,
    'signdate': "2020-04-05",
    'signature': signature
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

test_moxy_assessment = {
                "vl_side" : "right",
                "performance_metric_2_value": 100,
                "starting_thb": 11,
                "limiter": "Demand",
                "recovery_baseline": 50,
                "gas_tank_size": 75,
                "starting_sm_o2": 99,
                "intervention": "notes on notes",
                "performance_metric_1": "Feet/Min",
                "performance_metric_2": "Lbs",
                "performance_metric_1_value": 1000,
                "performance_baseline": 89,
                "notes": "just some notes"
}

test_heart_assessment = {
  "co2_tolerance": 60,
  "resting_hr": 55,
  "estimated_vo2_max": 84,
  "notes": "some noty notes",
  "max_hr": 200,
  "theoretical_max_hr": 209,
  "avg_training_hr": 145,
  "avg_eval_hr": 110
}

test_strength_assessment = {
    "clientid": 0,
    "upper_push": {
    "right": {
      "estimated_10rm": 250,
      "attempt_1": 12,
      "attempt_2": 10,
      "attempt_3": 5,
      "weight": 200
    },
    "notes": "more notes",
    "left": {
      "estimated_10rm": 260,
      "attempt_1": 15,
      "attempt_2": 15,
      "attempt_3": 10,
      "weight": 200
    },
    "bilateral": {
      "estimated_10rm": 260,
      "attempt_1": 15,
      "attempt_2": 15,
      "attempt_3": 0,
      "weight": 200
    }
  },
  "upper_pull": {
    "right": {
      "estimated_10rm": 250,
      "attempt_1": 12,
      "attempt_2": 10,
      "attempt_3": 5,
      "weight": 200
    },
    "notes": "string",
    "left": {
      "estimated_10rm": 250,
      "attempt_1": 12,
      "attempt_2": 10,
      "attempt_3": 5,
      "weight": 200
    },
    "bilateral": {
      "estimated_10rm": 260,
      "attempt_1": 15,
      "attempt_2": 15,
      "attempt_3": 0,
      "weight": 200
    }
  }
}

test_power_assessment = {
  "leg_press": {
    "bilateral": {
      "attempt_1": 21,
      "attempt_2": 12,
      "attempt_3": 10,
      "weight": 550,
      "average": 0
    },
    "right": {
      "attempt_1": 22,
      "attempt_2": 16,
      "attempt_3": 5,
      "weight": 220,
      "average": 0
    },
    "left": {
      "attempt_1": 22,
      "attempt_2": 16,
      "attempt_3": 5,
      "weight": 220,
      "average": 0
    }
  },
  "lower_watts_per_kg": 100,
  "upper_watts_per_kg": 60,
  "push_pull": {
    "right": {
      "attempt_1": 16,
      "attempt_2": 10,
      "attempt_3": 0,
      "weight": 50,
      "average": 0
    },
    "left": {
      "attempt_1": 16,
      "attempt_2": 10,
      "attempt_3": 0,
      "weight": 50,
      "average": 0
    }
  }
}

test_movement_assessment = {
  "toe_touch": {
    "ribcage_movement": [
      "Even Bilaterally"
    ],
    "notes": "string",
    "pelvis_movement": [
      "Right Hip High",
      "Left Hip High"
    ],
    "depth": "string"
  },
  "squat": {
    "eye_test": True,
    "depth": "string",
    "can_breathe": True,
    "can_look_up": True,
    "ramp": "string"
  },
  "standing_rotation": {
    "left": {
      "notes": "string"
    },
    "right": {
      "notes": "string"
    }
  }
}

test_chessboard_assessment = {
  "notes": "notes",
  "isa_structure": "Asymmetrical Atypical",
  "isa_movement": "Dynamic",
  "hip": {
    "left": {
      "er": 0,
      "add": 0,
      "slr": 0,
      "flexion": 0,
      "ir": 0,
      "extension": 0,
      "abd": 0
    },
    "right": {
      "er": 0,
      "add": 0,
      "slr": 0,
      "flexion": 0,
      "ir": 0,
      "extension": 0,
      "abd": 0
    }
  },
  "shoulder": {
    "left": {
      "er": 0,
      "add": 0,
      "flexion": 0,
      "ir": 0,
      "extension": 0,
      "abd": 0
    },
    "right": {
      "er": 0,
      "add": 0,
      "flexion": 0,
      "ir": 0,
      "extension": 0,
      "abd": 0
    }
  }
}

test_lung_assessment = {
  "breaths_per_minute": 67,
  "max_minute_volume": 409,
  "notes": "little struggle but overall fine",
  "liters_min_kg": 74,
  "bag_size": 6,
  "duration": 150
}

test_moxy_rip = {
        "vl_side": "left",
        "recovery_baseline_smo2": 0,
        "performance": {
            "two": {
            "smo2": 0,
            "avg_power": 0,
            "thb": 10,
            "hr_max_min": 180
            },
            "one": {
            "smo2": 0,
            "avg_power": 0,
            "thb": 10,
            "hr_max_min": 140
            },
            "three": {
            "smo2": 0,
            "avg_power": 0,
            "thb": 10,
            "hr_max_min": 150
            },
            "four": {
            "smo2": 0,
            "avg_power": 0,
            "thb": 10,
            "hr_max_min": 120
            }
        },
        "recovery": {
            "two": {
            "smo2": 60,
            "avg_power": 60,
            "thb": 10,
            "hr_max_min": 60
            },
            "one": {
            "smo2": 20,
            "avg_power": 100,
            "thb": 10,
            "hr_max_min": 70
            },
            "three": {
            "smo2":50,
            "avg_power": 90,
            "thb": 10,
            "hr_max_min": 70
            },
            "four": {
            "smo2": 50,
            "avg_power": 80,
            "thb": 10,
            "hr_max_min": 70
            }
        },
        "performance_baseline_smo2": 50,
        "performance_baseline_thb": 10,
        "thb_tank_size": 10,
        "avg_watt_kg": 10,
        "recovery_baseline_thb": 10,
        "avg_interval_time": 50,
        "avg_recovery_time": 56,
        "smo2_tank_size": 60,
          "limiter": "Demand",
        "intervention": "just fine for now"
}

test_pt_history = {
    "exercise": "olympic weigthlifting",
    "has_pt": False,
    "has_chiro": True,
    "has_massage": False,
    "has_surgery": True,
    "has_medication": False,
    "has_acupuncture": True,
    "pain_areas": "here",
    "best_pain": 7,
    "worst_pain": 1,
    "current_pain": 4,
    "makes_worse": "exercise",
    "makes_better": "also exercise"
}

test_medical_history = {
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

test_medical_physical = {
  "cardiac_rrr": True,
  "cardiac_murmurs_info": "string",
  "abdominal_bowel": True,
  "abdominal_hsm": True,
  "cardiac_murmurs": True,
  "abdominal_hard": True,
  "vital_respiratoryrate": 5,
  "vital_temperature": 98,
  "vital_heartrate": 70,
  "pulmonary_wheezing_info": "string",
  "cardiac_gallops": True,
  "vital_height_inches": 100,
  "cardiac_rubs": True,
  "abdominal_hsm_info": "string",
  "cardiac_s1s2": False,
  "abdominal_soft": False,
  "vital_diastolic": 120,
  "pulmonary_rhonchi": False,
  "vital_weight": 110,
  "pulmonary_wheezing": False,
  "pulmonary_clear": False,
  "vital_systolic": 70,
  "notes": "string",
  "pulmonary_rales": False
}

test_fitness_questionnaire = {
  "stress_sources_notes": "many things stress me out",
  "sleep_hours": "6-8",
  "energy_level": 5,
  "libido_level": 2,
  "stress_level": 4,
  "obstacles_expected": "mostly motivating myself consistently",
  "confidence_level": 4,
  "clientid": 0,
  "physical_goals_other": "",
  "stress_sources": [
    "Family",
    "Finances",
    "Social Obligations"
  ],
  "trainer_expectation_other": "",
  "lifestyle_goals_other": "just want to get into a routine",
  "trainer_expectation": "Expertise",
  "physical_goals_notes": "I want to be fit",
  "lifestyle_goals_notes": "doing fine for now",
  "current_fitness_level": 6,
  "lifestyle_goals": [
    "Increased Energy",
    "Other"
  ],
  "physical_goals": [
    "Weight Loss",
    "Increase Strength"
  ],
  "sleep_quality_level": 2,
  "obstacles_likely": True,
  "stress_sources_other": "",
  "goal_fitness_level": 9
}

test_blood_chemistry_cbc = {
    "idx": 1,
    "clientid": 1,
    "exam_date": "2020-09-01",
    "rbc": 3,
    "hemoglobin": 4,
    "hematocrit": 5,
    "mcv": 60,
    "mch": 7,
    "mchc": 8,
    "rdw": 9,
    "wbc": 10,
    "rel_neutrophils": 11,
    "abs_neutrophils": 12,
    "rel_lymphocytes": 13,
    "abs_lymphocytes": 16,
    "rel_monocytes": 15,
    "abs_monocytes": 16,
    "rel_eosinophils": 17,
    "abs_eosinophils": 18,
    "basophils": 19,
    "platelets": 20
}