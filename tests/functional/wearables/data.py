from datetime import datetime, timedelta
from dateutil import parser

wearables_data = {
    'has_freestyle': True,
    'has_fitbit': True,
    'has_oura': True,
    'has_applewatch': True,
    'registered_freestyle': False,
    'registered_fitbit': False,
    'registered_oura': False,
    'registered_applewatch': False}

wearables_freestyle_data = {
    'activation_timestamp': '2020-04-05T12:34:56.000',
    'glucose': [1.1, 2.2, 3.3],
    'timestamps': [
        '2020-04-05T01:00:12.345678',
        '2020-04-05T02:00:00.000',
        '2020-04-05T03:00:00.000']}

wearables_freestyle_more_data = {
    'activation_timestamp': '2020-04-05T12:34:56.000',
    'glucose': [2.2, 3.3, 4.4, 5.5],
    'timestamps': [
        '2020-04-05T02:00:00.000',
        '2020-04-05T03:00:00.000',
        '2020-04-05T04:00:00.000',
        '2020-04-05T05:00:00.000']}

# Combine previous two to check against merge
wearables_freestyle_combo_data = {
    'activation_timestamp': '2020-04-05T12:34:56.000',
    'glucose': [1.1, 2.2, 3.3, 4.4, 5.5],
    'timestamps': [
        '2020-04-05T01:00:12.345678',
        '2020-04-05T02:00:00.000',
        '2020-04-05T03:00:00.000',
        '2020-04-05T04:00:00.000',
        '2020-04-05T05:00:00.000']}

wearables_freestyle_empty_data = {
    'activation_timestamp': '2020-04-05T12:34:56.000',
    'glucose': [],
    'timestamps': []}

wearables_freestyle_unequal_data = {
    'activation_timestamp': '2020-04-05T12:34:56.000',
    'glucose': [6.6, 7.7, 8.8],
    'timestamps': [
        '2020-04-05T06:00:00.000',
        '2020-04-05T07:00:00.000']}

wearables_freestyle_duplicate_data = {
    'activation_timestamp': '2020-04-05T12:34:56.000',
    'glucose': [6.6, 7.7, 7.7],
    'timestamps': [
        '2020-04-05T06:00:00.000',
        '2020-04-05T07:00:00.000',
        '2020-04-05T07:00:00.000']}

BLOOD_GLUCOSE_WEARABLE = 'FREESTYLELIBRE'
BLOOD_PRESSURE_WEARABLE = 'OMRON'
DATETIME_NOW = datetime.utcnow()
DATETIME_NOW_HOUR_0 = DATETIME_NOW.replace(hour=0)
DATETIME_MINUS_THREE_WEEKS = (datetime.utcnow() - timedelta(weeks=3))
DATETIME_MINUS_THREE_WEEKS_HOUR_7 = DATETIME_MINUS_THREE_WEEKS.replace(hour=7)

blood_glucose_data_1 = {
    "user_id": 17,
    "wearable": BLOOD_GLUCOSE_WEARABLE,
    "data": {
        "body": {
            "testField": 1.0,
            "testFieldAgain": 2.0,
            "glucose_data": {
                "day_avg_blood_glucose_mg_per_dL": 120.0,
                "blood_glucose_samples": [
                    {
                        "timestamp": datetime.utcnow(),
                        "blood_glucose_mg_per_dL": 100.0
                    },
                    {
                        "timestamp": datetime.utcnow(),
                        "blood_glucose_mg_per_dL": 150.0
                    }
                ]
            }
        }
    },
    "timestamp": datetime.utcnow()
}

blood_glucose_data_2 = {
    "user_id": 17,
    "wearable": BLOOD_GLUCOSE_WEARABLE,
    "data": {
        "body": {
            "testField": 1.0,
            "testFieldAgain": 2.0,
            "glucose_data": {
                "day_avg_blood_glucose_mg_per_dL": 90.0,
                "blood_glucose_samples": [
                    {
                        "timestamp": (datetime.utcnow() - timedelta(weeks=3)),
                        "blood_glucose_mg_per_dL": 90.0
                    },
                    {
                        "timestamp": (datetime.utcnow() - timedelta(weeks=3)),
                        "blood_glucose_mg_per_dL": 110.0
                    }
                ]
            }
        }
    },
    "timestamp": (datetime.utcnow() - timedelta(weeks=3))
}


BLOOD_PRESSURE_WEARABLE = 'OMRONUS'

now = datetime.utcnow()
one_hour_ago = now - timedelta(hours=1)
one_day_ago = now - timedelta(days=1)
two_days_ago = now - timedelta(days=2)
three_days_ago = now - timedelta(days=3)
five_weeks_ago = now - timedelta(weeks=5)
six_weeks_ago = now - timedelta(weeks=6)
seven_weeks_ago = now - timedelta(weeks=7)
eight_weeks_ago = now - timedelta(weeks=8)

test_8100_data_past_week = {
    "user_id": None,
    "wearable": BLOOD_PRESSURE_WEARABLE,
    "timestamp": three_days_ago,
    "data": {
        "body": {
            "blood_pressure_data": {
                "blood_pressure_samples": [
                    {
                        "timestamp": three_days_ago,
                        "diastolic_bp": 68,
                        "systolic_bp": 119
                    },
                    {
                        "timestamp": two_days_ago,
                        "diastolic_bp": 78,
                        "systolic_bp": 127
                    },
                    {
                        "timestamp": one_day_ago,
                        "diastolic_bp": 71,
                        "systolic_bp": 137
                    },
                    {
                        "timestamp": one_hour_ago,
                        "diastolic_bp": 69,
                        "systolic_bp": 142
                    },
                ]
            },
        }
    }
}

test_8100_data_week_to_month_ago = {
    "user_id": None,
    "wearable": BLOOD_PRESSURE_WEARABLE,
    "timestamp": five_weeks_ago,
    "data": {
        "body": {
            "blood_pressure_data": {
                "blood_pressure_samples": [
                    {
                        "timestamp": eight_weeks_ago,
                        "diastolic_bp": 68,
                        "systolic_bp": 107
                    },
                    {
                        "timestamp": seven_weeks_ago,
                        "diastolic_bp": 87,
                        "systolic_bp": 124
                    },
                    {
                        "timestamp": six_weeks_ago,
                        "diastolic_bp": 67,
                        "systolic_bp": 128
                    },
                    {
                        "timestamp": five_weeks_ago,
                        "diastolic_bp": 96,
                        "systolic_bp": 146
                    },
                ]
            },
        }
    }
}

blood_pressure_data_1 = {
    "user_id" : 17,
    "wearable" : BLOOD_PRESSURE_WEARABLE,
    "data" : {
        "body" : {
            "testField" : 1.0,
            "testFieldAgain" : 2.0,
            "heart_data" : {
                "detailed" : {
                    "hr_samples" : [
                        {
                            "bpm" : 90.0,
                            "timestamp" : DATETIME_NOW_HOUR_0
                        },
                        {
                            "bpm" : 155.0,
                            "timestamp" : DATETIME_NOW_HOUR_0
                        }
                    ]
                }
            },
            "blood_pressure_data" : {
                "blood_pressure_samples" : [
                    {
                        "systolic_bp" : 70.0,
                        "diastolic_bp" : 140.0,
                        "timestamp" : DATETIME_NOW_HOUR_0
                    },
                    {
                        "systolic_bp" : 85.0,
                        "diastolic_bp" : 135.0,
                        "timestamp" : DATETIME_NOW_HOUR_0
                    }
                ]
            }
        }
    },
    "timestamp" : DATETIME_NOW_HOUR_0
}

blood_pressure_data_2 = {
    "user_id" : 17,
    "wearable" : BLOOD_PRESSURE_WEARABLE,
    "data" : {
        "body" : {
            "testField" : 1.0,
            "testFieldAgain" : 2.0,
            "heart_data" : {
                "detailed" : {
                    "hr_samples" : [
                        {
                            "bpm" : 100.0,
                            "timestamp" : DATETIME_MINUS_THREE_WEEKS_HOUR_7
                        },
                        {
                            "bpm" : 120.0,
                            "timestamp" : DATETIME_MINUS_THREE_WEEKS_HOUR_7
                        }
                    ]
                }
            },
            "blood_pressure_data" : {
                "blood_pressure_samples" : [
                    {
                        "systolic_bp" : 90.0,
                        "diastolic_bp" : 120.0,
                        "timestamp" : DATETIME_MINUS_THREE_WEEKS_HOUR_7
                    },
                    {
                        "systolic_bp" : 80.0,
                        "diastolic_bp" : 130.0,
                        "timestamp" : DATETIME_MINUS_THREE_WEEKS_HOUR_7
                    }
                ]
            }
        }
    },
    "timestamp" : DATETIME_MINUS_THREE_WEEKS_HOUR_7
}

wearables_fitbit_data_1 = {
  "user_id": 17,
  "wearable": "FITBIT",
  "data": {
    "Activity": {
      "calories_data": {
        "net_intake_calories": 200,
        "BMR_calories": 1000,
        "total_burned_calories": 30,
        "net_activity_calories": 92
      },
      "heart_rate_data": {
        "summary": {
          "max_hr_bpm": 20,
          "resting_hr_bpm": 11,
          "avg_hrv_rmssd": 3,
          "min_hr_bpm": 4,
          "user_max_hr_bpm": 5,
          "avg_hrv_sdnn": 6,
          "avg_hr_bpm": 6
        }
      }
    }
  },
  "timestamp": datetime.utcnow()
}

wearables_fitbit_data_2 = {
  "user_id": 17,
  "wearable": "FITBIT",
  "data": {
    "Athlete": {
      "age": 10,
      "country": "US",
      "bio": "None",
      "state": "TX",
      "last_name": "Focker",
      "sex": "M",
      "city": "Houston",
      "email": "test_email@email.com",
      "date_of_birth": "01/20/1964",
      "first_name": "Bernie"
    }
  },
  "timestamp": (datetime.utcnow() - timedelta(weeks=2))
}

sample_cmg_data = {
    "timestamp": parser.parse("2023-04-14T05:00:00.000Z"),
    "user_id": 17,
    "wearable": "FREESTYLELIBRE",
    "data": {
        "body": {
        "glucose_data": {
            "detailed_blood_glucose_samples": [],
            "blood_glucose_samples": [
                {
                    "blood_glucose_mg_per_dL": 40,
                    "timestamp": parser.parse("2023-04-14T05:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 50,
                    "timestamp": parser.parse("2023-04-14T05:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 51,
                    "timestamp": parser.parse("2023-04-14T05:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 54,
                    "timestamp": parser.parse("2023-04-14T06:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 59,
                    "timestamp": parser.parse("2023-04-14T06:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 66,
                    "timestamp": parser.parse("2023-04-14T07:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 70,
                    "timestamp": parser.parse("2023-04-14T07:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 74,
                    "timestamp": parser.parse("2023-04-14T08:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 79,
                    "timestamp": parser.parse("2023-04-14T08:45:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 84,
                    "timestamp": parser.parse("2023-04-14T09:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 99,
                    "timestamp": parser.parse("2023-04-14T09:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 110,
                    "timestamp": parser.parse("2023-04-14T10:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 120,
                    "timestamp": parser.parse("2023-04-14T10:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 128,
                    "timestamp": parser.parse("2023-04-14T11:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 135,
                    "timestamp": parser.parse("2023-04-14T11:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 144,
                    "timestamp": parser.parse("2023-04-14T11:45:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 151,
                    "timestamp": parser.parse("2023-04-14T12:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 160,
                    "timestamp": parser.parse("2023-04-14T12:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 166,
                    "timestamp": parser.parse("2023-04-14T13:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 166,
                    "timestamp": parser.parse("2023-04-14T13:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 170,
                    "timestamp": parser.parse("2023-04-14T13:45:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 175,
                    "timestamp": parser.parse("2023-04-14T14:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 179,
                    "timestamp": parser.parse("2023-04-14T14:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 181,
                    "timestamp": parser.parse("2023-04-14T15:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 183,
                    "timestamp": parser.parse("2023-04-14T16:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 188,
                    "timestamp": parser.parse("2023-04-14T16:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 190,
                    "timestamp": parser.parse("2023-04-14T17:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 158,
                    "timestamp": parser.parse("2023-04-14T17:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 151,
                    "timestamp": parser.parse("2023-04-14T18:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 160,
                    "timestamp": parser.parse("2023-04-14T18:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 166,
                    "timestamp": parser.parse("2023-04-14T19:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 165,
                    "timestamp": parser.parse("2023-04-14T19:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 159,
                    "timestamp": parser.parse("2023-04-14T19:45:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 155,
                    "timestamp": parser.parse("2023-04-14T20:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 151,
                    "timestamp": parser.parse("1970-01-01T00:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 160,
                    "timestamp": parser.parse("2023-04-14T21:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 170,
                    "timestamp": parser.parse("2023-04-14T21:45:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 190,
                    "timestamp": parser.parse("2023-04-14T22:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 199,
                    "timestamp": parser.parse("2023-04-14T23:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 200,
                    "timestamp": parser.parse("2023-04-14T23:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 220,
                    "timestamp": parser.parse("2023-04-15T00:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 260,
                    "timestamp": parser.parse("2023-04-15T00:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 270,
                    "timestamp": parser.parse("2023-04-15T01:00:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 279,
                    "timestamp": parser.parse("2023-04-15T01:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 278,
                    "timestamp": parser.parse("2023-04-15T02:15:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 189,
                    "timestamp": parser.parse("2023-04-15T03:30:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 177,
                    "timestamp": parser.parse("2023-04-15T03:45:00.000Z")
                },
                {
                    "blood_glucose_mg_per_dL": 160,
                    "timestamp": parser.parse("2023-04-15T04:00:00.000Z")
                }
                ],
                "day_avg_blood_glucose_mg_per_dL": 151.8541667
            }
        }
    }
}
