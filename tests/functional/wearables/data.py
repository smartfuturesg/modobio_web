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
BLOOD_PRESSURE_WEARABLE = 'OMRON'
DATETIME_NOW = datetime.utcnow()
DATETIME_NOW_HOUR_18 = DATETIME_NOW.replace(hour=18)
DATETIME_MINUS_THREE_WEEKS = (datetime.utcnow() - timedelta(weeks=3))
DATETIME_MINUS_THREE_WEEKS_HOUR_7 = DATETIME_MINUS_THREE_WEEKS.replace(hour=7)

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
                            "timestamp" : DATETIME_NOW_HOUR_18
                        },
                        {
                            "bpm" : 155.0,
                            "timestamp" : DATETIME_NOW_HOUR_18
                        }
                    ]
                }
            },
            "blood_pressure_data" : {
                "blood_pressure_samples" : [
                    {
                        "systolic_bp" : 70.0,
                        "diastolic_bp" : 140.0,
                        "timestamp" : DATETIME_NOW_HOUR_18
                    },
                    {
                        "systolic_bp" : 85.0,
                        "diastolic_bp" : 135.0,
                        "timestamp" : DATETIME_NOW_HOUR_18
                    }
                ]
            }
        }
    },
    "date" : DATETIME_NOW_HOUR_18
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
    "date" : DATETIME_MINUS_THREE_WEEKS_HOUR_7
}
