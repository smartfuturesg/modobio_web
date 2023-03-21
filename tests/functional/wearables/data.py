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

BLOOD_PRESSURE_WEARABLE = 'OMRON'

# this is how terra data is actually store in OUR mongo
# for data in response.get_json()['data']:
#     # Update existing or create new doc (upsert).
#     result = mongo.db.wearables.update_one(
#         {'user_id': user_id, 'wearable': wearable, 'timestamp': data['metadata']['start_time']},
#         {'$set': {f'data.{data_type}': data}},
#         upsert=True)

test_8100_data_1 = {
    "user_id": None,
    "wearable": BLOOD_PRESSURE_WEARABLE,
    "timestamp": "2023-03-21T07:58:39.812905+00:00",
    "data": {
        "body": {
            "blood_pressure_data": {
                "blood_pressure_samples": [
                    {
                        "timestamp": "2023-03-21T07:58:39.812905+00:00",
                        "diastolic_bp": 68.33630592176382,
                        "systolic_bp": 119.19867497456774
                    },
                    {
                        "timestamp": "2023-03-21T08:04:39.812905+00:00",
                        "diastolic_bp": 73.3760192475188,
                        "systolic_bp": 127.9531023369045
                    },
                    {
                        "timestamp": "2023-03-21T08:10:39.812905+00:00",
                        "diastolic_bp": 71.44922696001048,
                        "systolic_bp": 137.9793511515013
                    },
                    {
                        "timestamp": "2023-03-21T08:16:39.812905+00:00",
                        "diastolic_bp": 69.81319560682198,
                        "systolic_bp": 142.49936593554165
                    },
                    {
                        "timestamp": "2023-03-21T08:22:39.812905+00:00",
                        "diastolic_bp": 78.16936804081661,
                        "systolic_bp": 114.74266723680435
                    },
                    {
                        "timestamp": "2023-03-21T08:28:39.812905+00:00",
                        "diastolic_bp": 62.5342966175853,
                        "systolic_bp": 121.63209790302301
                    },
                    {
                        "timestamp": "2023-03-21T08:34:39.812905+00:00",
                        "diastolic_bp": 65.65018211594425,
                        "systolic_bp": 125.89360031655082
                    }
                ]
            },
        }
    }
}

test_8100_data_2 = {
    "user_id": None,
    "wearable": BLOOD_PRESSURE_WEARABLE,
    "timestamp": "2023-03-21T07:28:46.501002+00:00",
    "data": {
        "body": {
            "blood_pressure_data": {
                "blood_pressure_samples": [
                    {
                        "timestamp": "2023-03-21T07:28:46.501002+00:00",
                        "diastolic_bp": 96.66579727748561,
                        "systolic_bp": 146.58850876823806
                    },
                    {
                        "timestamp": "2023-03-21T07:40:46.501002+00:00",
                        "diastolic_bp": 67.3294429368544,
                        "systolic_bp": 128.60105668902614
                    },
                    {
                        "timestamp": "2023-03-21T07:52:46.501002+00:00",
                        "diastolic_bp": 87.79067389650139,
                        "systolic_bp": 124.34609472361335
                    },
                    {
                        "timestamp": "2023-03-21T08:04:46.501002+00:00",
                        "diastolic_bp": 68.15334488420415,
                        "systolic_bp": 107.19440094427837
                    }
                ]
            },
        }
    }
}
