from datetime import datetime, timedelta

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

blood_glucose_data_1 = {
    "user_id" : 17,
    "wearable" : BLOOD_GLUCOSE_WEARABLE,
    "data" : {
        "body" : {
            "testField" : 1.0,
            "testFieldAgain" : 2.0,
            "glucose_data" : {
                "day_avg_blood_glucose_mg_per_dL" : 120.0,
                "blood_glucose_samples" : [
                    {
                        "timestamp" : datetime.utcnow(),
                        "blood_glucose_mg_per_dL" : 100.0
                    },
                    {
                        "timestamp" : datetime.utcnow(),
                        "blood_glucose_mg_per_dL" : 150.0
                    }
                ]
            }
        }
    },
    "date" : datetime.utcnow()
}

blood_glucose_data_2 = {
    "user_id" : 17,
    "wearable" : BLOOD_GLUCOSE_WEARABLE,
    "data" : {
        "body" : {
            "testField" : 1.0,
            "testFieldAgain" : 2.0,
            "glucose_data" : {
                "day_avg_blood_glucose_mg_per_dL" : 90.0,
                "blood_glucose_samples" : [
                    {
                        "timestamp" : (datetime.utcnow() - timedelta(weeks=3)),
                        "blood_glucose_mg_per_dL" : 90.0
                    },
                    {
                        "timestamp" : (datetime.utcnow() - timedelta(weeks=3)),
                        "blood_glucose_mg_per_dL" : 110.0
                    }
                ]
            }
        }
    },
    "date" : (datetime.utcnow() - timedelta(weeks=3))
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
  "date": datetime.utcnow()
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
  "date": (datetime.utcnow() - timedelta(weeks=2))
}