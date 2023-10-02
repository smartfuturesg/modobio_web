from datetime import datetime, timedelta
from dateutil import parser

wearables_data = {
    "has_freestyle": True,
    "has_fitbit": True,
    "has_oura": True,
    "has_applewatch": True,
    "registered_freestyle": False,
    "registered_fitbit": False,
    "registered_oura": False,
    "registered_applewatch": False,
}

wearables_freestyle_data = {
    "activation_timestamp": "2020-04-05T12:34:56.000",
    "glucose": [1.1, 2.2, 3.3],
    "timestamps": [
        "2020-04-05T01:00:12.345678",
        "2020-04-05T02:00:00.000",
        "2020-04-05T03:00:00.000",
    ],
}

wearables_freestyle_more_data = {
    "activation_timestamp": "2020-04-05T12:34:56.000",
    "glucose": [2.2, 3.3, 4.4, 5.5],
    "timestamps": [
        "2020-04-05T02:00:00.000",
        "2020-04-05T03:00:00.000",
        "2020-04-05T04:00:00.000",
        "2020-04-05T05:00:00.000",
    ],
}

# Combine previous two to check against merge
wearables_freestyle_combo_data = {
    "activation_timestamp": "2020-04-05T12:34:56.000",
    "glucose": [1.1, 2.2, 3.3, 4.4, 5.5],
    "timestamps": [
        "2020-04-05T01:00:12.345678",
        "2020-04-05T02:00:00.000",
        "2020-04-05T03:00:00.000",
        "2020-04-05T04:00:00.000",
        "2020-04-05T05:00:00.000",
    ],
}

wearables_freestyle_empty_data = {
    "activation_timestamp": "2020-04-05T12:34:56.000",
    "glucose": [],
    "timestamps": [],
}

wearables_freestyle_unequal_data = {
    "activation_timestamp": "2020-04-05T12:34:56.000",
    "glucose": [6.6, 7.7, 8.8],
    "timestamps": ["2020-04-05T06:00:00.000", "2020-04-05T07:00:00.000"],
}

wearables_freestyle_duplicate_data = {
    "activation_timestamp": "2020-04-05T12:34:56.000",
    "glucose": [6.6, 7.7, 7.7],
    "timestamps": [
        "2020-04-05T06:00:00.000",
        "2020-04-05T07:00:00.000",
        "2020-04-05T07:00:00.000",
    ],
}

BLOOD_GLUCOSE_WEARABLE = "FREESTYLELIBRE"
BLOOD_PRESSURE_WEARABLE = "OMRON"
DATETIME_NOW = datetime.utcnow()
DATETIME_NOW_HOUR_0 = DATETIME_NOW.replace(hour=0)
DATETIME_MINUS_THREE_WEEKS = datetime.utcnow() - timedelta(weeks=3)
DATETIME_MINUS_THREE_WEEKS_HOUR_7 = DATETIME_MINUS_THREE_WEEKS.replace(hour=7)

blood_glucose_data_1 = {
    "user_id": 16,
    "wearable": BLOOD_GLUCOSE_WEARABLE,
    "data": {
        "body": {
            "testField": 1.0,
            "testFieldAgain": 2.0,
            "glucose_data": {
                "day_avg_blood_glucose_mg_per_dL": 120.0,
                "blood_glucose_samples": [
                    {"timestamp": datetime.utcnow(), "blood_glucose_mg_per_dL": 100.0},
                    {"timestamp": datetime.utcnow(), "blood_glucose_mg_per_dL": 150.0},
                ],
            },
        }
    },
    "timestamp": datetime.utcnow(),
}

blood_glucose_data_2 = {
    "user_id": 16,
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
                        "blood_glucose_mg_per_dL": 90.0,
                    },
                    {
                        "timestamp": (datetime.utcnow() - timedelta(weeks=3)),
                        "blood_glucose_mg_per_dL": 110.0,
                    },
                ],
            },
        }
    },
    "timestamp": (datetime.utcnow() - timedelta(weeks=3)),
}


BLOOD_PRESSURE_WEARABLE = "OMRONUS"

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
                        "systolic_bp": 119,
                    },
                    {"timestamp": two_days_ago, "diastolic_bp": 78, "systolic_bp": 127},
                    {"timestamp": one_day_ago, "diastolic_bp": 71, "systolic_bp": 137},
                    {"timestamp": one_hour_ago, "diastolic_bp": 69, "systolic_bp": 142},
                ]
            },
            "heart_data": {
                "heart_rate_data": {
                    "detailed": {
                        "hr_samples": [
                            {"bpm": 65, "timestamp": three_days_ago},
                            {"bpm": 61, "timestamp": two_days_ago},
                            {"bpm": 63, "timestamp": one_day_ago},
                            {"bpm": 61, "timestamp": one_hour_ago},
                        ]
                    },
                },
            },
        }
    },
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
                        "systolic_bp": 107,
                    },
                    {
                        "timestamp": seven_weeks_ago,
                        "diastolic_bp": 87,
                        "systolic_bp": 124,
                    },
                    {
                        "timestamp": six_weeks_ago,
                        "diastolic_bp": 67,
                        "systolic_bp": 128,
                    },
                    {
                        "timestamp": five_weeks_ago,
                        "diastolic_bp": 96,
                        "systolic_bp": 146,
                    },
                ]
            },
            "heart_data": {
                "heart_rate_data": {
                    "detailed": {
                        "hr_samples": [
                            {"bpm": 63, "timestamp": eight_weeks_ago},
                            {"bpm": 59, "timestamp": seven_weeks_ago},
                            {"bpm": 69, "timestamp": six_weeks_ago},
                            {"bpm": 72, "timestamp": five_weeks_ago},
                        ]
                    },
                },
            },
        }
    },
}

blood_pressure_data_1 = {
    "user_id": 16,
    "wearable": BLOOD_PRESSURE_WEARABLE,
    "data": {
        "body": {
            "testField": 1.0,
            "testFieldAgain": 2.0,
            "heart_data": {
                "heart_rate_data": {
                    "detailed": {
                        "hr_samples": [
                            {"bpm": 90.0, "timestamp": DATETIME_NOW_HOUR_0},
                            {"bpm": 155.0, "timestamp": DATETIME_NOW_HOUR_0},
                        ]
                    }
                }
            },
            "blood_pressure_data": {
                "blood_pressure_samples": [
                    {
                        "systolic_bp": 70.0,
                        "diastolic_bp": 140.0,
                        "timestamp": DATETIME_NOW_HOUR_0,
                    },
                    {
                        "systolic_bp": 85.0,
                        "diastolic_bp": 135.0,
                        "timestamp": DATETIME_NOW_HOUR_0,
                    },
                ]
            },
        }
    },
    "timestamp": DATETIME_NOW_HOUR_0,
}

blood_pressure_data_2 = {
    "user_id": 16,
    "wearable": BLOOD_PRESSURE_WEARABLE,
    "data": {
        "body": {
            "testField": 1.0,
            "testFieldAgain": 2.0,
            "heart_data": {
                "heart_rate_data": {
                    "detailed": {
                        "hr_samples": [
                            {
                                "bpm": 100.0,
                                "timestamp": DATETIME_MINUS_THREE_WEEKS_HOUR_7,
                            },
                            {
                                "bpm": 120.0,
                                "timestamp": DATETIME_MINUS_THREE_WEEKS_HOUR_7,
                            },
                        ]
                    }
                }
            },
            "blood_pressure_data": {
                "blood_pressure_samples": [
                    {
                        "systolic_bp": 90.0,
                        "diastolic_bp": 120.0,
                        "timestamp": DATETIME_MINUS_THREE_WEEKS_HOUR_7,
                    },
                    {
                        "systolic_bp": 80.0,
                        "diastolic_bp": 130.0,
                        "timestamp": DATETIME_MINUS_THREE_WEEKS_HOUR_7,
                    },
                ]
            },
        }
    },
    "timestamp": DATETIME_MINUS_THREE_WEEKS_HOUR_7,
}

wearables_fitbit_data_1 = {
    "user_id": 16,
    "wearable": "FITBIT",
    "data": {
        "Activity": {
            "calories_data": {
                "net_intake_calories": 200,
                "BMR_calories": 1000,
                "total_burned_calories": 30,
                "net_activity_calories": 92,
            },
            "heart_rate_data": {
                "summary": {
                    "max_hr_bpm": 20,
                    "resting_hr_bpm": 11,
                    "avg_hrv_rmssd": 3,
                    "min_hr_bpm": 4,
                    "user_max_hr_bpm": 5,
                    "avg_hrv_sdnn": 6,
                    "avg_hr_bpm": 6,
                }
            },
        }
    },
    "timestamp": datetime.utcnow(),
}

wearables_fitbit_data_2 = {
    "user_id": 16,
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
            "first_name": "Bernie",
        }
    },
    "timestamp": (datetime.utcnow() - timedelta(weeks=2)),
}

sample_cmg_data = {
    "timestamp": parser.parse("2023-04-14T05:00:00.000Z"),
    "user_id": 16,
    "wearable": "FREESTYLELIBRE",
    "data": {
        "body": {
            "glucose_data": {
                "detailed_blood_glucose_samples": [],
                "blood_glucose_samples": [
                    {
                        "blood_glucose_mg_per_dL": 40,
                        "timestamp": parser.parse("2023-04-14T05:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 50,
                        "timestamp": parser.parse("2023-04-14T05:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 51,
                        "timestamp": parser.parse("2023-04-14T05:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 54,
                        "timestamp": parser.parse("2023-04-14T06:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 59,
                        "timestamp": parser.parse("2023-04-14T06:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 66,
                        "timestamp": parser.parse("2023-04-14T07:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 70,
                        "timestamp": parser.parse("2023-04-14T07:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 74,
                        "timestamp": parser.parse("2023-04-14T08:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 79,
                        "timestamp": parser.parse("2023-04-14T08:45:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 84,
                        "timestamp": parser.parse("2023-04-14T09:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 99,
                        "timestamp": parser.parse("2023-04-14T09:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 110,
                        "timestamp": parser.parse("2023-04-14T10:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 120,
                        "timestamp": parser.parse("2023-04-14T10:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 128,
                        "timestamp": parser.parse("2023-04-14T11:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 135,
                        "timestamp": parser.parse("2023-04-14T11:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 144,
                        "timestamp": parser.parse("2023-04-14T11:45:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 151,
                        "timestamp": parser.parse("2023-04-14T12:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 160,
                        "timestamp": parser.parse("2023-04-14T12:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 166,
                        "timestamp": parser.parse("2023-04-14T13:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 166,
                        "timestamp": parser.parse("2023-04-14T13:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 170,
                        "timestamp": parser.parse("2023-04-14T13:45:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 175,
                        "timestamp": parser.parse("2023-04-14T14:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 179,
                        "timestamp": parser.parse("2023-04-14T14:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 181,
                        "timestamp": parser.parse("2023-04-14T15:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 183,
                        "timestamp": parser.parse("2023-04-14T16:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 188,
                        "timestamp": parser.parse("2023-04-14T16:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 190,
                        "timestamp": parser.parse("2023-04-14T17:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 158,
                        "timestamp": parser.parse("2023-04-14T17:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 151,
                        "timestamp": parser.parse("2023-04-14T18:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 160,
                        "timestamp": parser.parse("2023-04-14T18:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 166,
                        "timestamp": parser.parse("2023-04-14T19:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 165,
                        "timestamp": parser.parse("2023-04-14T19:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 159,
                        "timestamp": parser.parse("2023-04-14T19:45:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 155,
                        "timestamp": parser.parse("2023-04-14T20:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 151,
                        "timestamp": parser.parse("1970-01-01T00:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 160,
                        "timestamp": parser.parse("2023-04-14T21:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 170,
                        "timestamp": parser.parse("2023-04-14T21:45:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 190,
                        "timestamp": parser.parse("2023-04-14T22:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 199,
                        "timestamp": parser.parse("2023-04-14T23:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 200,
                        "timestamp": parser.parse("2023-04-14T23:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 220,
                        "timestamp": parser.parse("2023-04-15T00:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 260,
                        "timestamp": parser.parse("2023-04-15T00:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 270,
                        "timestamp": parser.parse("2023-04-15T01:00:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 279,
                        "timestamp": parser.parse("2023-04-15T01:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 278,
                        "timestamp": parser.parse("2023-04-15T02:15:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 189,
                        "timestamp": parser.parse("2023-04-15T03:30:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 177,
                        "timestamp": parser.parse("2023-04-15T03:45:00.000Z"),
                    },
                    {
                        "blood_glucose_mg_per_dL": 160,
                        "timestamp": parser.parse("2023-04-15T04:00:00.000Z"),
                    },
                ],
                "day_avg_blood_glucose_mg_per_dL": 151.8541667,
            }
        }
    },
}


oura_wearable_daily_and_sleep_data = [
    {
        "_id": "6501eed9ab0cb7214bafee16",
        "timestamp": parser.parse("2023-09-12T23:47:30.000+0000"),
        "user_id": 16,
        "wearable": "OURA",
        "data": {
            "sleep": {
                "metadata": {
                    "upload_type": 0,
                    "is_nap": False,
                    "start_time": parser.parse("2023-09-12T23:47:30.000+0000"),
                    "end_time": parser.parse("2023-09-13T07:55:30.000+0000"),
                    "tz_offset": -25200.0,
                },
                "respiration_data": {
                    "snoring_data": {
                        "num_snoring_events": None,
                        "samples": [],
                        "end_time": None,
                        "start_time": None,
                        "total_snoring_duration_seconds": None,
                    },
                    "oxygen_saturation_data": {
                        "avg_saturation_percentage": None,
                        "samples": [],
                        "start_time": None,
                        "end_time": None,
                    },
                    "breaths_data": {
                        "avg_breaths_per_min": 16.875,
                        "samples": [],
                        "min_breaths_per_min": None,
                        "on_demand_reading": None,
                        "max_breaths_per_min": None,
                        "start_time": None,
                        "end_time": None,
                    },
                },
                "temperature_data": {"delta": -0.15},
                "sleep_durations_data": {
                    "awake": {
                        "duration_short_interruption_seconds": None,
                        "duration_awake_state_seconds": 3030,
                        "num_wakeup_events": 7,
                        "wake_up_latency_seconds": 600,
                        "duration_long_interruption_seconds": None,
                        "num_out_of_bed_events": None,
                        "sleep_latency_seconds": 300,
                    },
                    "sleep_efficiency": 0.9,
                    "hypnogram_samples": [
                        {
                            "timestamp": parser.parse("2023-09-12T23:47:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T23:52:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T23:57:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:02:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:07:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:12:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:17:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:22:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:27:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:32:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:37:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:42:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:47:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:52:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T00:57:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:02:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:07:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:12:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:17:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:22:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:27:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:32:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:37:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:42:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:47:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:52:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T01:57:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:02:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:07:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:12:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:17:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:22:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:27:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:32:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:37:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:42:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:47:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:52:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T02:57:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:02:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:07:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:12:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:17:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:22:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:27:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:32:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:37:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:42:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:47:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:52:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T03:57:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:02:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:07:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:12:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:17:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:22:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:27:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:32:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:37:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:42:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:47:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:52:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T04:57:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:02:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:07:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:12:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:17:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:22:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:27:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:32:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:37:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:42:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:47:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:52:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T05:57:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:02:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:07:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:12:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:17:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:22:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:27:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:32:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:37:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:42:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:47:30.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:52:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T06:57:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:02:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:07:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:12:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:17:30.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:22:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:27:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:32:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:37:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:42:30.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:47:30.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-13T07:52:30.000+0000"),
                            "level": 1,
                        },
                    ],
                    "asleep": {
                        "duration_asleep_state_seconds": 26250,
                        "duration_deep_sleep_state_seconds": 6540,
                        "num_REM_events": 7,
                        "duration_REM_sleep_state_seconds": 4740,
                        "duration_light_sleep_state_seconds": 14970,
                    },
                    "other": {
                        "duration_unmeasurable_sleep_seconds": None,
                        "duration_in_bed_seconds": 29280,
                    },
                },
                "device_data": {
                    "manufacturer": None,
                    "hardware_version": None,
                    "name": None,
                    "data_provided": [],
                    "software_version": None,
                    "serial_number": None,
                    "activation_timestamp": None,
                    "other_devices": [],
                },
                "readiness_data": {"recovery_level": 5, "readiness": 89},
                "heart_rate_data": {
                    "summary": {
                        "resting_hr_bpm": 54,
                        "avg_hrv_sdnn": None,
                        "user_max_hr_bpm": None,
                        "avg_hr_bpm": 58.5,
                        "min_hr_bpm": 54,
                        "max_hr_bpm": 65.0,
                        "avg_hrv_rmssd": 39,
                    },
                    "detailed": {
                        "hr_samples": [
                            {
                                "bpm": 65.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T23:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T23:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T23:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:37:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T00:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:37:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T01:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:37:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T02:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:37:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T03:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:37:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T04:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:37:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T05:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:37:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:47:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:52:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T06:57:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:02:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:07:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:12:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:17:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:22:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:27:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:32:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:42:30.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-13T07:47:30.000+0000"
                                ),
                            },
                        ],
                        "hrv_samples_rmssd": [
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T23:47:30.000+0000"
                                ),
                                "hrv_rmssd": 22.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T23:52:30.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T23:57:30.000+0000"
                                ),
                                "hrv_rmssd": 25.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:02:30.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:07:30.000+0000"
                                ),
                                "hrv_rmssd": 20.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:12:30.000+0000"
                                ),
                                "hrv_rmssd": 24.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:17:30.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:22:30.000+0000"
                                ),
                                "hrv_rmssd": 29.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:27:30.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:32:30.000+0000"
                                ),
                                "hrv_rmssd": 29.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:37:30.000+0000"
                                ),
                                "hrv_rmssd": 25.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:42:30.000+0000"
                                ),
                                "hrv_rmssd": 25.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:47:30.000+0000"
                                ),
                                "hrv_rmssd": 29.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:52:30.000+0000"
                                ),
                                "hrv_rmssd": 27.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T00:57:30.000+0000"
                                ),
                                "hrv_rmssd": 46.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:02:30.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:07:30.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:12:30.000+0000"
                                ),
                                "hrv_rmssd": 34.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:17:30.000+0000"
                                ),
                                "hrv_rmssd": 24.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:22:30.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:27:30.000+0000"
                                ),
                                "hrv_rmssd": 24.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:32:30.000+0000"
                                ),
                                "hrv_rmssd": 24.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:37:30.000+0000"
                                ),
                                "hrv_rmssd": 21.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:42:30.000+0000"
                                ),
                                "hrv_rmssd": 23.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:47:30.000+0000"
                                ),
                                "hrv_rmssd": 48.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:52:30.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T01:57:30.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:02:30.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:07:30.000+0000"
                                ),
                                "hrv_rmssd": 50.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:12:30.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:17:30.000+0000"
                                ),
                                "hrv_rmssd": 47.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:22:30.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:27:30.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:32:30.000+0000"
                                ),
                                "hrv_rmssd": 29.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:37:30.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:42:30.000+0000"
                                ),
                                "hrv_rmssd": 35.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:47:30.000+0000"
                                ),
                                "hrv_rmssd": 31.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:52:30.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T02:57:30.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:02:30.000+0000"
                                ),
                                "hrv_rmssd": 50.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:07:30.000+0000"
                                ),
                                "hrv_rmssd": 54.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:12:30.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:17:30.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:22:30.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:27:30.000+0000"
                                ),
                                "hrv_rmssd": 35.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:32:30.000+0000"
                                ),
                                "hrv_rmssd": 39.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:37:30.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:42:30.000+0000"
                                ),
                                "hrv_rmssd": 43.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:47:30.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:52:30.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T03:57:30.000+0000"
                                ),
                                "hrv_rmssd": 43.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:02:30.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:07:30.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:12:30.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:17:30.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:22:30.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:27:30.000+0000"
                                ),
                                "hrv_rmssd": 43.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:32:30.000+0000"
                                ),
                                "hrv_rmssd": 50.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:37:30.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:42:30.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:47:30.000+0000"
                                ),
                                "hrv_rmssd": 54.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:52:30.000+0000"
                                ),
                                "hrv_rmssd": 54.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T04:57:30.000+0000"
                                ),
                                "hrv_rmssd": 55.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:02:30.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:07:30.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:12:30.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:17:30.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:22:30.000+0000"
                                ),
                                "hrv_rmssd": 52.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:27:30.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:32:30.000+0000"
                                ),
                                "hrv_rmssd": 51.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:37:30.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:42:30.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:47:30.000+0000"
                                ),
                                "hrv_rmssd": 47.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:52:30.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T05:57:30.000+0000"
                                ),
                                "hrv_rmssd": 52.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:02:30.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:07:30.000+0000"
                                ),
                                "hrv_rmssd": 64.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:12:30.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:17:30.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:22:30.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:27:30.000+0000"
                                ),
                                "hrv_rmssd": 29.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:32:30.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:37:30.000+0000"
                                ),
                                "hrv_rmssd": 25.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:42:30.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:47:30.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:52:30.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T06:57:30.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:02:30.000+0000"
                                ),
                                "hrv_rmssd": 52.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:07:30.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:12:30.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:17:30.000+0000"
                                ),
                                "hrv_rmssd": 51.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:22:30.000+0000"
                                ),
                                "hrv_rmssd": 54.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:27:30.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:32:30.000+0000"
                                ),
                                "hrv_rmssd": 34.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:42:30.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-13T07:47:30.000+0000"
                                ),
                                "hrv_rmssd": 61.0,
                            },
                        ],
                        "hrv_samples_sdnn": [],
                    },
                },
            }
        },
    },
    {
        "_id": "6500baadab0cb7214baf22dc",
        "timestamp": parser.parse("2023-09-12T00:00:00.000+0000"),
        "user_id": 16,
        "wearable": "OURA",
        "data": {
            "daily": {
                "device_data": {
                    "software_version": None,
                    "other_devices": [],
                    "name": None,
                    "hardware_version": None,
                    "manufacturer": None,
                    "data_provided": [],
                    "activation_timestamp": None,
                    "serial_number": None,
                },
                "strain_data": {"strain_level": None},
                "distance_data": {
                    "elevation": {
                        "loss_actual_meters": None,
                        "gain_actual_meters": None,
                        "max_meters": None,
                        "min_meters": None,
                        "gain_planned_meters": None,
                        "avg_meters": None,
                    },
                    "distance_meters": 4012,
                    "detailed": {
                        "distance_samples": [],
                        "step_samples": [],
                        "floors_climbed_samples": [],
                        "elevation_samples": [],
                    },
                    "steps": 4216,
                    "floors_climbed": None,
                    "swimming": {
                        "num_strokes": None,
                        "num_laps": None,
                        "pool_length_meters": None,
                    },
                },
                "calories_data": {
                    "calorie_samples": [],
                    "net_activity_calories": 146,
                    "BMR_calories": None,
                    "net_intake_calories": None,
                    "total_burned_calories": 1522,
                },
                "heart_rate_data": {
                    "summary": {
                        "avg_hr_bpm": None,
                        "max_hr_bpm": None,
                        "user_max_hr_bpm": None,
                        "avg_hrv_rmssd": None,
                        "avg_hrv_sdnn": None,
                        "hr_zone_data": [],
                        "resting_hr_bpm": None,
                        "min_hr_bpm": None,
                    },
                    "detailed": {
                        "hrv_samples_sdnn": [],
                        "hrv_samples_rmssd": [],
                        "hr_samples": [],
                    },
                },
                "stress_data": {
                    "avg_stress_level": None,
                    "high_stress_duration_seconds": None,
                    "medium_stress_duration_seconds": None,
                    "stress_duration_seconds": None,
                    "low_stress_duration_seconds": None,
                    "max_stress_level": None,
                    "activity_stress_duration_seconds": None,
                    "samples": [],
                    "rest_stress_duration_seconds": None,
                },
                "oxygen_data": {
                    "vo2max_ml_per_min_per_kg": None,
                    "vo2_samples": [],
                    "avg_saturation_percentage": None,
                    "saturation_samples": [],
                },
                "active_durations_data": {
                    "standing_hours_count": None,
                    "activity_levels_samples": [],
                    "activity_seconds": 10260,
                    "vigorous_intensity_seconds": 0,
                    "low_intensity_seconds": 9360,
                    "rest_seconds": 32460,
                    "inactivity_seconds": 11340,
                    "moderate_intensity_seconds": 900,
                    "num_continuous_inactive_periods": 0,
                    "standing_seconds": None,
                },
                "MET_data": {
                    "num_moderate_intensity_minutes": 48,
                    "num_low_intensity_minutes": 120,
                    "MET_samples": [
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:00:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:01:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:02:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:03:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:04:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:05:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T04:06:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T04:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:08:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:10:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T04:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:15:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T04:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:18:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T04:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:22:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T04:23:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T04:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:25:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:26:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:28:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:29:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:31:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T04:32:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:34:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T04:35:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T04:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:37:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T04:38:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T04:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:40:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T04:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:56:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:57:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T04:58:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T04:59:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:00:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:01:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T05:02:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T05:03:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T05:04:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:05:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:06:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:08:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:10:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T05:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:14:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T05:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:17:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T05:18:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:23:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:25:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:26:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T05:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:28:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:29:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T05:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:31:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:32:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:34:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T05:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:37:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:38:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:40:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T05:41:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T05:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:47:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T05:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:52:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T05:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:56:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:57:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:58:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T05:59:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:00:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T06:01:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T06:02:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:03:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:04:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T06:05:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:06:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:08:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:18:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:23:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:25:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T06:26:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:28:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:29:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:31:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:32:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T06:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:34:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T06:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:37:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:38:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:40:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:48:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T06:49:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T06:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:54:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T06:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:56:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T06:57:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T06:58:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T06:59:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:00:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:01:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:02:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:03:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T07:04:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:05:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:06:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:08:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:09:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T07:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:18:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:23:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:25:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:26:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:28:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:29:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:31:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:32:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:34:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:37:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:38:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:40:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T07:56:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T07:57:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T07:58:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T07:59:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:00:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:01:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T08:02:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:03:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T08:04:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T08:05:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:06:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T08:07:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T08:08:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T08:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:18:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T08:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:20:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T08:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T08:23:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T08:24:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T08:25:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T08:26:00.000+0000"),
                        },
                        {
                            "level": 4.4,
                            "timestamp": parser.parse("2023-09-12T08:27:00.000+0000"),
                        },
                        {
                            "level": 3.0,
                            "timestamp": parser.parse("2023-09-12T08:28:00.000+0000"),
                        },
                        {
                            "level": 2.0,
                            "timestamp": parser.parse("2023-09-12T08:29:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T08:30:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T08:31:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T08:32:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T08:33:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:34:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:35:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T08:36:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T08:37:00.000+0000"),
                        },
                        {
                            "level": 2.2,
                            "timestamp": parser.parse("2023-09-12T08:38:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:39:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T08:40:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T08:41:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T08:42:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:43:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:44:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:45:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:46:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:47:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:48:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:49:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:50:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T08:51:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:52:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:53:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:54:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:55:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:56:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T08:57:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T08:58:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T08:59:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T09:00:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T09:01:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:02:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T09:03:00.000+0000"),
                        },
                        {
                            "level": 3.5,
                            "timestamp": parser.parse("2023-09-12T09:04:00.000+0000"),
                        },
                        {
                            "level": 3.3,
                            "timestamp": parser.parse("2023-09-12T09:05:00.000+0000"),
                        },
                        {
                            "level": 3.0,
                            "timestamp": parser.parse("2023-09-12T09:06:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T09:07:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T09:08:00.000+0000"),
                        },
                        {
                            "level": 3.9,
                            "timestamp": parser.parse("2023-09-12T09:09:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T09:10:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T09:11:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T09:12:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T09:13:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:14:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T09:15:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T09:16:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T09:17:00.000+0000"),
                        },
                        {
                            "level": 2.0,
                            "timestamp": parser.parse("2023-09-12T09:18:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T09:19:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T09:20:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T09:21:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:22:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:23:00.000+0000"),
                        },
                        {
                            "level": 3.7,
                            "timestamp": parser.parse("2023-09-12T09:24:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T09:25:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T09:26:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T09:27:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T09:28:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T09:29:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T09:30:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:31:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T09:32:00.000+0000"),
                        },
                        {
                            "level": 2.8,
                            "timestamp": parser.parse("2023-09-12T09:33:00.000+0000"),
                        },
                        {
                            "level": 3.4,
                            "timestamp": parser.parse("2023-09-12T09:34:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T09:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T09:36:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T09:37:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T09:38:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T09:39:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:40:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T09:41:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:42:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T09:43:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T09:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T09:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T09:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T10:09:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:10:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:11:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:12:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:13:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:14:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T10:15:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:16:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T10:17:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:18:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:19:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:20:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:21:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T10:22:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T10:23:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T10:24:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T10:25:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T10:26:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T10:27:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:28:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T10:29:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:30:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T10:31:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T10:32:00.000+0000"),
                        },
                        {
                            "level": 2.0,
                            "timestamp": parser.parse("2023-09-12T10:33:00.000+0000"),
                        },
                        {
                            "level": 2.9,
                            "timestamp": parser.parse("2023-09-12T10:34:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T10:35:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T10:36:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:37:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T10:38:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T10:39:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:40:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T10:41:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T10:42:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T10:43:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T10:44:00.000+0000"),
                        },
                        {
                            "level": 4.6,
                            "timestamp": parser.parse("2023-09-12T10:45:00.000+0000"),
                        },
                        {
                            "level": 2.2,
                            "timestamp": parser.parse("2023-09-12T10:46:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T10:47:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:48:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:49:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:50:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:51:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T10:52:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T10:53:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T10:54:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:55:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:56:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T10:57:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:58:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T10:59:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T11:00:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:01:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:02:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:03:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T11:04:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T11:05:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:06:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:07:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:08:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:09:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T11:10:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T11:11:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:12:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:13:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:14:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T11:15:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T11:16:00.000+0000"),
                        },
                        {
                            "level": 2.7,
                            "timestamp": parser.parse("2023-09-12T11:17:00.000+0000"),
                        },
                        {
                            "level": 2.4,
                            "timestamp": parser.parse("2023-09-12T11:18:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T11:19:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:20:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T11:21:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T11:22:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T11:23:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T11:24:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T11:25:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T11:26:00.000+0000"),
                        },
                        {
                            "level": 3.2,
                            "timestamp": parser.parse("2023-09-12T11:27:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T11:28:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T11:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T11:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T12:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T13:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T14:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T15:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T16:47:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T16:48:00.000+0000"),
                        },
                        {
                            "level": 4.0,
                            "timestamp": parser.parse("2023-09-12T16:49:00.000+0000"),
                        },
                        {
                            "level": 5.0,
                            "timestamp": parser.parse("2023-09-12T16:50:00.000+0000"),
                        },
                        {
                            "level": 6.3,
                            "timestamp": parser.parse("2023-09-12T16:51:00.000+0000"),
                        },
                        {
                            "level": 5.3,
                            "timestamp": parser.parse("2023-09-12T16:52:00.000+0000"),
                        },
                        {
                            "level": 4.8,
                            "timestamp": parser.parse("2023-09-12T16:53:00.000+0000"),
                        },
                        {
                            "level": 4.6,
                            "timestamp": parser.parse("2023-09-12T16:54:00.000+0000"),
                        },
                        {
                            "level": 2.4,
                            "timestamp": parser.parse("2023-09-12T16:55:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T16:56:00.000+0000"),
                        },
                        {
                            "level": 3.5,
                            "timestamp": parser.parse("2023-09-12T16:57:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T16:58:00.000+0000"),
                        },
                        {
                            "level": 5.9,
                            "timestamp": parser.parse("2023-09-12T16:59:00.000+0000"),
                        },
                        {
                            "level": 7.7,
                            "timestamp": parser.parse("2023-09-12T17:00:00.000+0000"),
                        },
                        {
                            "level": 3.4,
                            "timestamp": parser.parse("2023-09-12T17:01:00.000+0000"),
                        },
                        {
                            "level": 2.6,
                            "timestamp": parser.parse("2023-09-12T17:02:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T17:03:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T17:04:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T17:05:00.000+0000"),
                        },
                        {
                            "level": 2.2,
                            "timestamp": parser.parse("2023-09-12T17:06:00.000+0000"),
                        },
                        {
                            "level": 3.0,
                            "timestamp": parser.parse("2023-09-12T17:07:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T17:08:00.000+0000"),
                        },
                        {
                            "level": 3.5,
                            "timestamp": parser.parse("2023-09-12T17:09:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T17:10:00.000+0000"),
                        },
                        {
                            "level": 3.2,
                            "timestamp": parser.parse("2023-09-12T17:11:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T17:12:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T17:13:00.000+0000"),
                        },
                        {
                            "level": 2.9,
                            "timestamp": parser.parse("2023-09-12T17:14:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T17:15:00.000+0000"),
                        },
                        {
                            "level": 2.4,
                            "timestamp": parser.parse("2023-09-12T17:16:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T17:17:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T17:18:00.000+0000"),
                        },
                        {
                            "level": 4.4,
                            "timestamp": parser.parse("2023-09-12T17:19:00.000+0000"),
                        },
                        {
                            "level": 4.6,
                            "timestamp": parser.parse("2023-09-12T17:20:00.000+0000"),
                        },
                        {
                            "level": 3.2,
                            "timestamp": parser.parse("2023-09-12T17:21:00.000+0000"),
                        },
                        {
                            "level": 3.3,
                            "timestamp": parser.parse("2023-09-12T17:22:00.000+0000"),
                        },
                        {
                            "level": 2.0,
                            "timestamp": parser.parse("2023-09-12T17:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T17:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T18:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:40:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:41:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:42:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:43:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:44:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:45:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:46:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:47:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:48:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:49:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:50:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:51:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:52:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:53:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:54:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:55:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:56:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:57:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:58:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T19:59:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:00:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:01:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:02:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:03:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:04:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:05:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:06:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:07:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:08:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:09:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:10:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:11:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:12:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:13:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:14:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:15:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:16:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:17:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:18:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:19:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:20:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:21:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:22:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:23:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:24:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:25:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:26:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:27:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:28:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:29:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:30:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:31:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:32:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:33:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:34:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:35:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:36:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:37:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:38:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:39:00.000+0000"),
                        },
                        {
                            "level": 0.1,
                            "timestamp": parser.parse("2023-09-12T20:40:00.000+0000"),
                        },
                        {
                            "level": 2.8,
                            "timestamp": parser.parse("2023-09-12T20:41:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T20:42:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T20:43:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T20:44:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T20:45:00.000+0000"),
                        },
                        {
                            "level": 2.4,
                            "timestamp": parser.parse("2023-09-12T20:46:00.000+0000"),
                        },
                        {
                            "level": 2.7,
                            "timestamp": parser.parse("2023-09-12T20:47:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T20:48:00.000+0000"),
                        },
                        {
                            "level": 3.5,
                            "timestamp": parser.parse("2023-09-12T20:49:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T20:50:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T20:51:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T20:52:00.000+0000"),
                        },
                        {
                            "level": 3.8,
                            "timestamp": parser.parse("2023-09-12T20:53:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T20:54:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T20:55:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T20:56:00.000+0000"),
                        },
                        {
                            "level": 3.0,
                            "timestamp": parser.parse("2023-09-12T20:57:00.000+0000"),
                        },
                        {
                            "level": 2.6,
                            "timestamp": parser.parse("2023-09-12T20:58:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T20:59:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T21:00:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T21:01:00.000+0000"),
                        },
                        {
                            "level": 3.0,
                            "timestamp": parser.parse("2023-09-12T21:02:00.000+0000"),
                        },
                        {
                            "level": 3.5,
                            "timestamp": parser.parse("2023-09-12T21:03:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:04:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:05:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T21:06:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:07:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:08:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T21:09:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:10:00.000+0000"),
                        },
                        {
                            "level": 2.0,
                            "timestamp": parser.parse("2023-09-12T21:11:00.000+0000"),
                        },
                        {
                            "level": 3.7,
                            "timestamp": parser.parse("2023-09-12T21:12:00.000+0000"),
                        },
                        {
                            "level": 3.6,
                            "timestamp": parser.parse("2023-09-12T21:13:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T21:14:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T21:15:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T21:16:00.000+0000"),
                        },
                        {
                            "level": 4.0,
                            "timestamp": parser.parse("2023-09-12T21:17:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T21:18:00.000+0000"),
                        },
                        {
                            "level": 4.4,
                            "timestamp": parser.parse("2023-09-12T21:19:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:20:00.000+0000"),
                        },
                        {
                            "level": 4.0,
                            "timestamp": parser.parse("2023-09-12T21:21:00.000+0000"),
                        },
                        {
                            "level": 4.0,
                            "timestamp": parser.parse("2023-09-12T21:22:00.000+0000"),
                        },
                        {
                            "level": 4.0,
                            "timestamp": parser.parse("2023-09-12T21:23:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T21:24:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T21:25:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:26:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:27:00.000+0000"),
                        },
                        {
                            "level": 3.6,
                            "timestamp": parser.parse("2023-09-12T21:28:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T21:29:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T21:30:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T21:31:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T21:32:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T21:33:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T21:34:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T21:35:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T21:36:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T21:37:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T21:38:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T21:39:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T21:40:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:41:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T21:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:49:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T21:50:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T21:51:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T21:52:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T21:53:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T21:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T21:55:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T21:56:00.000+0000"),
                        },
                        {
                            "level": 2.6,
                            "timestamp": parser.parse("2023-09-12T21:57:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T21:58:00.000+0000"),
                        },
                        {
                            "level": 2.2,
                            "timestamp": parser.parse("2023-09-12T21:59:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:00:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:01:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:02:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:03:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:04:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T22:05:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:06:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:07:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T22:08:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T22:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:16:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:17:00.000+0000"),
                        },
                        {
                            "level": 1.5,
                            "timestamp": parser.parse("2023-09-12T22:18:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T22:19:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:20:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:21:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:22:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:23:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:24:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:25:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:26:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:27:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:28:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:29:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:30:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:31:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:32:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:33:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:34:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T22:35:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:36:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:37:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T22:38:00.000+0000"),
                        },
                        {
                            "level": 2.4,
                            "timestamp": parser.parse("2023-09-12T22:39:00.000+0000"),
                        },
                        {
                            "level": 3.5,
                            "timestamp": parser.parse("2023-09-12T22:40:00.000+0000"),
                        },
                        {
                            "level": 2.4,
                            "timestamp": parser.parse("2023-09-12T22:41:00.000+0000"),
                        },
                        {
                            "level": 1.8,
                            "timestamp": parser.parse("2023-09-12T22:42:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T22:43:00.000+0000"),
                        },
                        {
                            "level": 2.5,
                            "timestamp": parser.parse("2023-09-12T22:44:00.000+0000"),
                        },
                        {
                            "level": 2.1,
                            "timestamp": parser.parse("2023-09-12T22:45:00.000+0000"),
                        },
                        {
                            "level": 1.9,
                            "timestamp": parser.parse("2023-09-12T22:46:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:47:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:48:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:49:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:50:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T22:51:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:52:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T22:53:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T22:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T22:56:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T22:57:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T22:58:00.000+0000"),
                        },
                        {
                            "level": 1.6,
                            "timestamp": parser.parse("2023-09-12T22:59:00.000+0000"),
                        },
                        {
                            "level": 2.2,
                            "timestamp": parser.parse("2023-09-12T23:00:00.000+0000"),
                        },
                        {
                            "level": 2.4,
                            "timestamp": parser.parse("2023-09-12T23:01:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T23:02:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T23:03:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T23:04:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:05:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:06:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:07:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T23:08:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:16:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T23:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:18:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:21:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T23:22:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T23:23:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:25:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:26:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T23:27:00.000+0000"),
                        },
                        {
                            "level": 2.3,
                            "timestamp": parser.parse("2023-09-12T23:28:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:29:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:30:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:31:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T23:32:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T23:33:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-12T23:34:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T23:35:00.000+0000"),
                        },
                        {
                            "level": 1.4,
                            "timestamp": parser.parse("2023-09-12T23:36:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T23:37:00.000+0000"),
                        },
                        {
                            "level": 3.1,
                            "timestamp": parser.parse("2023-09-12T23:38:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:39:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-12T23:40:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T23:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:45:00.000+0000"),
                        },
                        {
                            "level": 1.7,
                            "timestamp": parser.parse("2023-09-12T23:46:00.000+0000"),
                        },
                        {
                            "level": 1.3,
                            "timestamp": parser.parse("2023-09-12T23:47:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-12T23:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:56:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:57:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:58:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-12T23:59:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:00:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:01:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:02:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:03:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:04:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:05:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T00:06:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:08:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:14:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T00:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:17:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-13T00:18:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:23:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:24:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T00:25:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-13T00:26:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:28:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:29:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:31:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:32:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:34:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:37:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T00:38:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:40:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:56:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:57:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:58:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T00:59:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:00:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:01:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:02:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:03:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:04:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:05:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:06:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:08:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:16:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T01:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:18:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-13T01:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:23:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:25:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:26:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:28:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:29:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:31:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:32:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:34:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:37:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:38:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:40:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:56:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:57:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T01:58:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T01:59:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:00:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:01:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:02:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-13T02:03:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:04:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:05:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:06:00.000+0000"),
                        },
                        {
                            "level": 1.0,
                            "timestamp": parser.parse("2023-09-13T02:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:08:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T02:09:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:18:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:21:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T02:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:23:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:25:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:26:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:28:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T02:29:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T02:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:31:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:32:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:34:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:37:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:38:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:40:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:56:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:57:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:58:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T02:59:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:00:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:01:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:02:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:03:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:04:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:05:00.000+0000"),
                        },
                        {
                            "level": 1.2,
                            "timestamp": parser.parse("2023-09-13T03:06:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:07:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:08:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T03:09:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T03:10:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:11:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:12:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:13:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:14:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:15:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:16:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:17:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:18:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:19:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:20:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:21:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:22:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:23:00.000+0000"),
                        },
                        {
                            "level": 1.1,
                            "timestamp": parser.parse("2023-09-13T03:24:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:25:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:26:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:27:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:28:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:29:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:30:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:31:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:32:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:33:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:34:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:35:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:36:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:37:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:38:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:39:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:40:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:41:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:42:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:43:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:44:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:45:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:46:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:47:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:48:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:49:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:50:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:51:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:52:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:53:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:54:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:55:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:56:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:57:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:58:00.000+0000"),
                        },
                        {
                            "level": 0.9,
                            "timestamp": parser.parse("2023-09-13T03:59:00.000+0000"),
                        },
                    ],
                    "avg_level": 1.25,
                    "num_high_intensity_minutes": 0,
                    "num_inactive_minutes": 3,
                },
                "metadata": {
                    "upload_type": 1,
                    "end_time": parser.parse("2023-09-13T00:00:00.000+0000"),
                    "start_time": parser.parse("2023-09-12T00:00:00.000+0000"),
                    "tz_offset": -25200.0,
                },
                "tag_data": {"tags": []},
                "scores": {"activity": 89, "sleep": 82, "recovery": 81},
            }
        },
    },
    {
        "_id": "6500b6adab0cb7214baf16b2",
        "timestamp": parser.parse("2023-09-11T23:29:46.000+0000"),
        "user_id": 16,
        "wearable": "OURA",
        "data": {
            "sleep": {
                "heart_rate_data": {
                    "detailed": {
                        "hrv_samples_rmssd": [
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T23:34:46.000+0000"
                                ),
                                "hrv_rmssd": 15.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T23:39:46.000+0000"
                                ),
                                "hrv_rmssd": 25.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T23:44:46.000+0000"
                                ),
                                "hrv_rmssd": 23.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T23:49:46.000+0000"
                                ),
                                "hrv_rmssd": 24.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T23:54:46.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T23:59:46.000+0000"
                                ),
                                "hrv_rmssd": 22.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:04:46.000+0000"
                                ),
                                "hrv_rmssd": 27.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:09:46.000+0000"
                                ),
                                "hrv_rmssd": 25.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:14:46.000+0000"
                                ),
                                "hrv_rmssd": 25.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:19:46.000+0000"
                                ),
                                "hrv_rmssd": 20.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:24:46.000+0000"
                                ),
                                "hrv_rmssd": 20.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:29:46.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:34:46.000+0000"
                                ),
                                "hrv_rmssd": 22.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:39:46.000+0000"
                                ),
                                "hrv_rmssd": 21.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:44:46.000+0000"
                                ),
                                "hrv_rmssd": 24.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:49:46.000+0000"
                                ),
                                "hrv_rmssd": 34.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:54:46.000+0000"
                                ),
                                "hrv_rmssd": 20.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T00:59:46.000+0000"
                                ),
                                "hrv_rmssd": 23.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:04:46.000+0000"
                                ),
                                "hrv_rmssd": 22.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:09:46.000+0000"
                                ),
                                "hrv_rmssd": 22.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:14:46.000+0000"
                                ),
                                "hrv_rmssd": 19.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:19:46.000+0000"
                                ),
                                "hrv_rmssd": 24.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:24:46.000+0000"
                                ),
                                "hrv_rmssd": 22.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:29:46.000+0000"
                                ),
                                "hrv_rmssd": 26.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:34:46.000+0000"
                                ),
                                "hrv_rmssd": 27.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:39:46.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:44:46.000+0000"
                                ),
                                "hrv_rmssd": 26.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:49:46.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:54:46.000+0000"
                                ),
                                "hrv_rmssd": 27.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T01:59:46.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:04:46.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:09:46.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:14:46.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:19:46.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:24:46.000+0000"
                                ),
                                "hrv_rmssd": 36.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:29:46.000+0000"
                                ),
                                "hrv_rmssd": 43.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:34:46.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:39:46.000+0000"
                                ),
                                "hrv_rmssd": 39.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:44:46.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:49:46.000+0000"
                                ),
                                "hrv_rmssd": 29.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:54:46.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T02:59:46.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:04:46.000+0000"
                                ),
                                "hrv_rmssd": 35.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:09:46.000+0000"
                                ),
                                "hrv_rmssd": 60.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:14:46.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:19:46.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:24:46.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:29:46.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:34:46.000+0000"
                                ),
                                "hrv_rmssd": 39.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:39:46.000+0000"
                                ),
                                "hrv_rmssd": 50.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:44:46.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:49:46.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:54:46.000+0000"
                                ),
                                "hrv_rmssd": 46.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T03:59:46.000+0000"
                                ),
                                "hrv_rmssd": 35.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:04:46.000+0000"
                                ),
                                "hrv_rmssd": 43.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:09:46.000+0000"
                                ),
                                "hrv_rmssd": 51.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:14:46.000+0000"
                                ),
                                "hrv_rmssd": 59.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:19:46.000+0000"
                                ),
                                "hrv_rmssd": 36.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:24:46.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:34:46.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:39:46.000+0000"
                                ),
                                "hrv_rmssd": 70.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:44:46.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:49:46.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:54:46.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T04:59:46.000+0000"
                                ),
                                "hrv_rmssd": 65.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:04:46.000+0000"
                                ),
                                "hrv_rmssd": 67.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:09:46.000+0000"
                                ),
                                "hrv_rmssd": 60.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:14:46.000+0000"
                                ),
                                "hrv_rmssd": 61.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:19:46.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:24:46.000+0000"
                                ),
                                "hrv_rmssd": 47.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:29:46.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:34:46.000+0000"
                                ),
                                "hrv_rmssd": 63.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:39:46.000+0000"
                                ),
                                "hrv_rmssd": 71.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:44:46.000+0000"
                                ),
                                "hrv_rmssd": 55.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:49:46.000+0000"
                                ),
                                "hrv_rmssd": 60.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:54:46.000+0000"
                                ),
                                "hrv_rmssd": 68.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T05:59:46.000+0000"
                                ),
                                "hrv_rmssd": 60.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:04:46.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:09:46.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:14:46.000+0000"
                                ),
                                "hrv_rmssd": 55.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:19:46.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:24:46.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:29:46.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:34:46.000+0000"
                                ),
                                "hrv_rmssd": 76.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:39:46.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:44:46.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:49:46.000+0000"
                                ),
                                "hrv_rmssd": 72.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:54:46.000+0000"
                                ),
                                "hrv_rmssd": 51.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T06:59:46.000+0000"
                                ),
                                "hrv_rmssd": 67.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:04:46.000+0000"
                                ),
                                "hrv_rmssd": 55.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:09:46.000+0000"
                                ),
                                "hrv_rmssd": 57.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:14:46.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:19:46.000+0000"
                                ),
                                "hrv_rmssd": 63.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:24:46.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:29:46.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:34:46.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:44:46.000+0000"
                                ),
                                "hrv_rmssd": 28.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-12T07:49:46.000+0000"
                                ),
                                "hrv_rmssd": 46.0,
                            },
                        ],
                        "hr_samples": [
                            {
                                "bpm": 69.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T23:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 67.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T23:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 65.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T23:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 65.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T23:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T23:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 65.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T23:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 65.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:29:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 65.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T00:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 65.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:29:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 64.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T01:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:29:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T02:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:29:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T03:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T04:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:29:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T05:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:29:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:39:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:49:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:54:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T06:59:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:04:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:09:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:14:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:19:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:24:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:29:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:34:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:44:46.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-12T07:49:46.000+0000"
                                ),
                            },
                        ],
                        "hrv_samples_sdnn": [],
                    },
                    "summary": {
                        "resting_hr_bpm": 54,
                        "avg_hrv_sdnn": None,
                        "user_max_hr_bpm": None,
                        "avg_hr_bpm": 60.625,
                        "min_hr_bpm": 54,
                        "avg_hrv_rmssd": 40,
                        "max_hr_bpm": 69.0,
                    },
                },
                "readiness_data": {"readiness": 81, "recovery_level": 5},
                "temperature_data": {"delta": 0.21},
                "device_data": {
                    "software_version": None,
                    "serial_number": None,
                    "name": None,
                    "other_devices": [],
                    "hardware_version": None,
                    "data_provided": [],
                    "manufacturer": None,
                    "activation_timestamp": None,
                },
                "sleep_durations_data": {
                    "hypnogram_samples": [
                        {
                            "timestamp": parser.parse("2023-09-11T23:29:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:34:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:39:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:44:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:49:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:54:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:59:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:04:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:09:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:14:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:19:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:24:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:29:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:34:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:39:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:44:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:49:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:54:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:59:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:04:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:09:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:14:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:19:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:24:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:29:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:34:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:39:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:44:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:49:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:54:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:59:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:04:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:09:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:14:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:19:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:24:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:29:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:34:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:39:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:44:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:49:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:54:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:59:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:04:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:09:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:14:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:19:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:24:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:29:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:34:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:39:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:44:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:49:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:54:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:59:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:04:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:09:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:14:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:19:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:24:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:29:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:34:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:39:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:44:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:49:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:54:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T04:59:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:04:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:09:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:14:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:19:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:24:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:29:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:34:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:39:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:44:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:49:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:54:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T05:59:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:04:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:09:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:14:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:19:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:24:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:29:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:34:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:39:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:44:46.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:49:46.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:54:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T06:59:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:04:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:09:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:14:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:19:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:24:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:29:46.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:34:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:39:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:44:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:49:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:54:46.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T07:59:46.000+0000"),
                            "level": 1,
                        },
                    ],
                    "awake": {
                        "duration_long_interruption_seconds": None,
                        "wake_up_latency_seconds": 300,
                        "num_wakeup_events": 9,
                        "sleep_latency_seconds": 1140,
                        "duration_awake_state_seconds": 2970,
                        "num_out_of_bed_events": None,
                        "duration_short_interruption_seconds": None,
                    },
                    "sleep_efficiency": 0.9,
                    "other": {
                        "duration_in_bed_seconds": 30900,
                        "duration_unmeasurable_sleep_seconds": None,
                    },
                    "asleep": {
                        "duration_light_sleep_state_seconds": 17460,
                        "duration_REM_sleep_state_seconds": 5130,
                        "num_REM_events": 7,
                        "duration_asleep_state_seconds": 27930,
                        "duration_deep_sleep_state_seconds": 5340,
                    },
                },
                "metadata": {
                    "upload_type": 0,
                    "is_nap": False,
                    "end_time": parser.parse("2023-09-12T08:04:46.000+0000"),
                    "start_time": parser.parse("2023-09-11T23:29:46.000+0000"),
                    "tz_offset": -25200.0,
                },
                "respiration_data": {
                    "breaths_data": {
                        "avg_breaths_per_min": 17.625,
                        "max_breaths_per_min": None,
                        "end_time": None,
                        "on_demand_reading": None,
                        "min_breaths_per_min": None,
                        "samples": [],
                        "start_time": None,
                    },
                    "oxygen_saturation_data": {
                        "end_time": None,
                        "samples": [],
                        "avg_saturation_percentage": None,
                        "start_time": None,
                    },
                    "snoring_data": {
                        "total_snoring_duration_seconds": None,
                        "num_snoring_events": None,
                        "end_time": None,
                        "samples": [],
                        "start_time": None,
                    },
                },
            }
        },
    },
    {
        "_id": "6500b6adab0cb7214baf16b0",
        "timestamp": parser.parse("2023-09-11T00:12:32.000+0000"),
        "user_id": 16,
        "wearable": "OURA",
        "data": {
            "sleep": {
                "heart_rate_data": {
                    "detailed": {
                        "hrv_samples_rmssd": [
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:17:32.000+0000"
                                ),
                                "hrv_rmssd": 26.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:22:32.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:27:32.000+0000"
                                ),
                                "hrv_rmssd": 39.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:32:32.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:37:32.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:42:32.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:47:32.000+0000"
                                ),
                                "hrv_rmssd": 31.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:52:32.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T00:57:32.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:02:32.000+0000"
                                ),
                                "hrv_rmssd": 35.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:07:32.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:12:32.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:17:32.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:22:32.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:27:32.000+0000"
                                ),
                                "hrv_rmssd": 36.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:32:32.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:42:32.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:47:32.000+0000"
                                ),
                                "hrv_rmssd": 39.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:52:32.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T01:57:32.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:02:32.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:07:32.000+0000"
                                ),
                                "hrv_rmssd": 36.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:12:32.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:17:32.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:22:32.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:27:32.000+0000"
                                ),
                                "hrv_rmssd": 34.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:32:32.000+0000"
                                ),
                                "hrv_rmssd": 29.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:37:32.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:42:32.000+0000"
                                ),
                                "hrv_rmssd": 37.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:47:32.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:52:32.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T02:57:32.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:02:32.000+0000"
                                ),
                                "hrv_rmssd": 36.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:07:32.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:12:32.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:17:32.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:22:32.000+0000"
                                ),
                                "hrv_rmssd": 43.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:27:32.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:32:32.000+0000"
                                ),
                                "hrv_rmssd": 36.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:37:32.000+0000"
                                ),
                                "hrv_rmssd": 41.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:42:32.000+0000"
                                ),
                                "hrv_rmssd": 35.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:47:32.000+0000"
                                ),
                                "hrv_rmssd": 39.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:52:32.000+0000"
                                ),
                                "hrv_rmssd": 34.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T03:57:32.000+0000"
                                ),
                                "hrv_rmssd": 32.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:02:32.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:07:32.000+0000"
                                ),
                                "hrv_rmssd": 33.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:12:32.000+0000"
                                ),
                                "hrv_rmssd": 31.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:17:32.000+0000"
                                ),
                                "hrv_rmssd": 30.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:22:32.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:27:32.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:32:32.000+0000"
                                ),
                                "hrv_rmssd": 39.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:37:32.000+0000"
                                ),
                                "hrv_rmssd": 42.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:42:32.000+0000"
                                ),
                                "hrv_rmssd": 38.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:47:32.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:52:32.000+0000"
                                ),
                                "hrv_rmssd": 48.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T04:57:32.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:02:32.000+0000"
                                ),
                                "hrv_rmssd": 48.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:07:32.000+0000"
                                ),
                                "hrv_rmssd": 46.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:12:32.000+0000"
                                ),
                                "hrv_rmssd": 57.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:17:32.000+0000"
                                ),
                                "hrv_rmssd": 49.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:22:32.000+0000"
                                ),
                                "hrv_rmssd": 51.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:27:32.000+0000"
                                ),
                                "hrv_rmssd": 51.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:32:32.000+0000"
                                ),
                                "hrv_rmssd": 48.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:37:32.000+0000"
                                ),
                                "hrv_rmssd": 50.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:42:32.000+0000"
                                ),
                                "hrv_rmssd": 45.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:47:32.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:52:32.000+0000"
                                ),
                                "hrv_rmssd": 46.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T05:57:32.000+0000"
                                ),
                                "hrv_rmssd": 54.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:02:32.000+0000"
                                ),
                                "hrv_rmssd": 52.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:07:32.000+0000"
                                ),
                                "hrv_rmssd": 50.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:17:32.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:22:32.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:27:32.000+0000"
                                ),
                                "hrv_rmssd": 40.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:32:32.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:37:32.000+0000"
                                ),
                                "hrv_rmssd": 67.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:42:32.000+0000"
                                ),
                                "hrv_rmssd": 76.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:47:32.000+0000"
                                ),
                                "hrv_rmssd": 64.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:52:32.000+0000"
                                ),
                                "hrv_rmssd": 56.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T06:57:32.000+0000"
                                ),
                                "hrv_rmssd": 66.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:02:32.000+0000"
                                ),
                                "hrv_rmssd": 60.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:07:32.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:12:32.000+0000"
                                ),
                                "hrv_rmssd": 54.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:17:32.000+0000"
                                ),
                                "hrv_rmssd": 61.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:22:32.000+0000"
                                ),
                                "hrv_rmssd": 68.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:27:32.000+0000"
                                ),
                                "hrv_rmssd": 78.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:32:32.000+0000"
                                ),
                                "hrv_rmssd": 73.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:37:32.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:42:32.000+0000"
                                ),
                                "hrv_rmssd": 70.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:47:32.000+0000"
                                ),
                                "hrv_rmssd": 64.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:52:32.000+0000"
                                ),
                                "hrv_rmssd": 60.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T07:57:32.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:02:32.000+0000"
                                ),
                                "hrv_rmssd": 58.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:07:32.000+0000"
                                ),
                                "hrv_rmssd": 51.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:12:32.000+0000"
                                ),
                                "hrv_rmssd": 52.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:17:32.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:22:32.000+0000"
                                ),
                                "hrv_rmssd": 50.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:27:32.000+0000"
                                ),
                                "hrv_rmssd": 44.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:32:32.000+0000"
                                ),
                                "hrv_rmssd": 53.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:37:32.000+0000"
                                ),
                                "hrv_rmssd": 70.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:42:32.000+0000"
                                ),
                                "hrv_rmssd": 60.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:47:32.000+0000"
                                ),
                                "hrv_rmssd": 65.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:52:32.000+0000"
                                ),
                                "hrv_rmssd": 63.0,
                            },
                            {
                                "timestamp": parser.parse(
                                    "2023-09-11T08:57:32.000+0000"
                                ),
                                "hrv_rmssd": 52.0,
                            },
                        ],
                        "hr_samples": [
                            {
                                "bpm": 63.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T00:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:12:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T01:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:12:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T02:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:12:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T03:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:12:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 60.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T04:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:12:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T05:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 62.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 61.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 53.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 52.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T06:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 53.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:12:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 53.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 53.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 53.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 53.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T07:57:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:02:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:07:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:12:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:17:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:22:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:27:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 58.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:32:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 56.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:37:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 54.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:42:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 55.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:47:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 57.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:52:32.000+0000"
                                ),
                            },
                            {
                                "bpm": 59.0,
                                "timestamp": parser.parse(
                                    "2023-09-11T08:57:32.000+0000"
                                ),
                            },
                        ],
                        "hrv_samples_sdnn": [],
                    },
                    "summary": {
                        "resting_hr_bpm": 52,
                        "avg_hrv_sdnn": None,
                        "user_max_hr_bpm": None,
                        "avg_hr_bpm": 59.125,
                        "min_hr_bpm": 52,
                        "avg_hrv_rmssd": 44,
                        "max_hr_bpm": 63.0,
                    },
                },
                "readiness_data": {"readiness": 85, "recovery_level": 5},
                "temperature_data": {"delta": -0.06},
                "device_data": {
                    "software_version": None,
                    "serial_number": None,
                    "name": None,
                    "other_devices": [],
                    "hardware_version": None,
                    "data_provided": [],
                    "manufacturer": None,
                    "activation_timestamp": None,
                },
                "sleep_durations_data": {
                    "hypnogram_samples": [
                        {
                            "timestamp": parser.parse("2023-09-11T00:12:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:17:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:22:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:27:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:32:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:37:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:42:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:47:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:52:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T00:57:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:02:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:07:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:12:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:17:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:22:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:27:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:32:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:37:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:42:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:47:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:52:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T01:57:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:02:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:07:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:12:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:17:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:22:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:27:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:32:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:37:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:42:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:47:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:52:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T02:57:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:02:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:07:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:12:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:17:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:22:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:27:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:32:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:37:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:42:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:47:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:52:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T03:57:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:02:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:07:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:12:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:17:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:22:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:27:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:32:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:37:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:42:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:47:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:52:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:57:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:02:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:07:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:12:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:17:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:22:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:27:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:32:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:37:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:42:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:47:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:52:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:57:32.000+0000"),
                            "level": 5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:02:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:07:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:12:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:17:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:22:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:27:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:32:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:37:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:42:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:47:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:52:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:57:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:02:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:07:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:12:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:17:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:22:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:27:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:32:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:37:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:42:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:47:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:52:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:57:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:02:32.000+0000"),
                            "level": 6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:07:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:12:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:17:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:22:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:27:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:32:32.000+0000"),
                            "level": 4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:37:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:42:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:47:32.000+0000"),
                            "level": 1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:52:32.000+0000"),
                            "level": 1,
                        },
                    ],
                    "awake": {
                        "duration_long_interruption_seconds": None,
                        "wake_up_latency_seconds": 1200,
                        "num_wakeup_events": 7,
                        "sleep_latency_seconds": 420,
                        "duration_awake_state_seconds": 3960,
                        "num_out_of_bed_events": None,
                        "duration_short_interruption_seconds": None,
                    },
                    "sleep_efficiency": 0.87,
                    "other": {
                        "duration_in_bed_seconds": 31500,
                        "duration_unmeasurable_sleep_seconds": None,
                    },
                    "asleep": {
                        "duration_light_sleep_state_seconds": 14670,
                        "duration_REM_sleep_state_seconds": 4380,
                        "num_REM_events": 7,
                        "duration_asleep_state_seconds": 27540,
                        "duration_deep_sleep_state_seconds": 8490,
                    },
                },
                "metadata": {
                    "upload_type": 0,
                    "is_nap": False,
                    "end_time": parser.parse("2023-09-11T08:57:32.000+0000"),
                    "start_time": parser.parse("2023-09-11T00:12:32.000+0000"),
                    "tz_offset": -25200.0,
                },
                "respiration_data": {
                    "breaths_data": {
                        "avg_breaths_per_min": 17.75,
                        "max_breaths_per_min": None,
                        "end_time": None,
                        "on_demand_reading": None,
                        "min_breaths_per_min": None,
                        "samples": [],
                        "start_time": None,
                    },
                    "oxygen_saturation_data": {
                        "end_time": None,
                        "samples": [],
                        "avg_saturation_percentage": None,
                        "start_time": None,
                    },
                    "snoring_data": {
                        "total_snoring_duration_seconds": None,
                        "num_snoring_events": None,
                        "end_time": None,
                        "samples": [],
                        "start_time": None,
                    },
                },
            }
        },
    },
    {
        "_id": "6500b6b0ab0cb7214baf16be",
        "timestamp": parser.parse("2023-09-11T00:00:00.000+0000"),
        "user_id": 16,
        "wearable": "OURA",
        "data": {
            "daily": {
                "metadata": {
                    "start_time": parser.parse("2023-09-11T00:00:00.000+0000"),
                    "end_time": parser.parse("2023-09-12T00:00:00.000+0000"),
                    "upload_type": 1,
                    "tz_offset": -25200.0,
                },
                "active_durations_data": {
                    "activity_seconds": 11100,
                    "activity_levels_samples": [],
                    "inactivity_seconds": 6840,
                    "vigorous_intensity_seconds": 5580,
                    "num_continuous_inactive_periods": 0,
                    "moderate_intensity_seconds": 300,
                    "rest_seconds": 33840,
                    "low_intensity_seconds": 5220,
                },
                "strain_data": {"strain_level": None},
                "MET_data": {
                    "MET_samples": [
                        {
                            "timestamp": parser.parse("2023-09-11T04:00:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:02:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:04:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:05:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:08:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:09:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:11:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:12:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:13:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:14:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:15:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:16:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:19:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:21:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:23:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:25:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:28:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:29:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:30:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:31:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:36:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:37:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:38:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:40:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:42:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:47:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:50:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:51:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T04:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:00:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:02:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:04:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:05:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:08:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:09:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:11:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:12:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:13:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:14:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:15:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:16:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:19:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:21:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:23:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:29:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:30:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:31:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:36:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:37:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:38:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:40:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:42:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:47:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:50:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T05:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:00:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:02:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:04:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:05:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:08:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:09:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:11:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:12:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:13:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:14:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:15:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:16:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:18:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:19:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:21:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:23:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:29:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:30:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:31:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:32:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:36:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:37:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:38:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:40:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:42:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:46:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:47:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:49:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:50:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:55:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T06:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:00:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:02:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:04:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:05:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:08:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:09:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:11:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:12:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:13:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:14:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:15:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:16:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:19:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:21:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:23:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:29:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:30:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:31:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:33:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:34:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:35:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:36:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:37:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:38:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:39:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:40:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:41:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:42:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:47:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:50:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:56:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T07:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:00:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:02:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:04:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:05:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:07:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:08:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:09:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:10:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:11:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:12:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:13:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:14:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:15:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:16:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:17:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:19:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:20:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:21:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:23:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:24:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:29:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:30:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:31:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:35:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:36:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:37:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:38:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:39:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:40:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:41:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:42:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:44:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:45:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:47:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:48:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:50:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:57:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:58:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T08:59:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:00:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:01:00.000+0000"),
                            "level": 1.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:02:00.000+0000"),
                            "level": 2.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:03:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:04:00.000+0000"),
                            "level": 2.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:05:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:06:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:07:00.000+0000"),
                            "level": 3.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:08:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:09:00.000+0000"),
                            "level": 2.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:10:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:11:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:12:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:13:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:14:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:15:00.000+0000"),
                            "level": 1.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:16:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:17:00.000+0000"),
                            "level": 2.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:18:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:19:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:20:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:21:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:22:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:23:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:24:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:25:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:26:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:27:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:28:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:29:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:30:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:31:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:32:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:33:00.000+0000"),
                            "level": 2.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:34:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:35:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:36:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:37:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:38:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:39:00.000+0000"),
                            "level": 2.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:40:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:41:00.000+0000"),
                            "level": 3.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:42:00.000+0000"),
                            "level": 2.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:43:00.000+0000"),
                            "level": 3.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:44:00.000+0000"),
                            "level": 5.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:45:00.000+0000"),
                            "level": 2.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:46:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:47:00.000+0000"),
                            "level": 3.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:48:00.000+0000"),
                            "level": 2.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:49:00.000+0000"),
                            "level": 3.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:50:00.000+0000"),
                            "level": 2.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:51:00.000+0000"),
                            "level": 3.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:52:00.000+0000"),
                            "level": 3.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:53:00.000+0000"),
                            "level": 2.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:54:00.000+0000"),
                            "level": 2.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:55:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:56:00.000+0000"),
                            "level": 1.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:57:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:58:00.000+0000"),
                            "level": 2.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T09:59:00.000+0000"),
                            "level": 2.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:00:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:01:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:02:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:03:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:04:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:05:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:06:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:07:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:08:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:09:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:10:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:11:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:12:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:13:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:14:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:15:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:16:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:17:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:18:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:19:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:20:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:21:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:22:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:23:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:24:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:25:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:29:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:30:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:31:00.000+0000"),
                            "level": 2.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:32:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:33:00.000+0000"),
                            "level": 2.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:34:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:35:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:36:00.000+0000"),
                            "level": 2.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:37:00.000+0000"),
                            "level": 4.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:38:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:39:00.000+0000"),
                            "level": 6.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:40:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:41:00.000+0000"),
                            "level": 4.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:42:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:43:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:44:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:45:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:46:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:47:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:48:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:49:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:50:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:51:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:52:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:53:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:54:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:55:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:56:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:57:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:58:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T10:59:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:00:00.000+0000"),
                            "level": 1.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:01:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:02:00.000+0000"),
                            "level": 1.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:03:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:04:00.000+0000"),
                            "level": 5.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:05:00.000+0000"),
                            "level": 5.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:06:00.000+0000"),
                            "level": 2.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:07:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:08:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:09:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:10:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:11:00.000+0000"),
                            "level": 1.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:12:00.000+0000"),
                            "level": 3.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:13:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:14:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:15:00.000+0000"),
                            "level": 2.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:16:00.000+0000"),
                            "level": 2.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:17:00.000+0000"),
                            "level": 3.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:18:00.000+0000"),
                            "level": 2.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:19:00.000+0000"),
                            "level": 2.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:20:00.000+0000"),
                            "level": 2.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:21:00.000+0000"),
                            "level": 2.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:22:00.000+0000"),
                            "level": 2.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:23:00.000+0000"),
                            "level": 3.5,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:24:00.000+0000"),
                            "level": 3.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:25:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:26:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:27:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:28:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:29:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:30:00.000+0000"),
                            "level": 2.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:31:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:32:00.000+0000"),
                            "level": 1.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:33:00.000+0000"),
                            "level": 2.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:34:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:35:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:36:00.000+0000"),
                            "level": 2.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:37:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:38:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:39:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:40:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:41:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T11:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T12:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T13:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T14:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T15:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:57:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:58:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T16:59:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:00:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:28:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:29:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:30:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:31:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:32:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:33:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:34:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:35:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:36:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:37:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:38:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:39:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:40:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:41:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:42:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:43:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:44:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:45:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:46:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:47:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:48:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:49:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:50:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:51:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:52:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:53:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:54:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:55:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:56:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:57:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:58:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T17:59:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:00:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:01:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:02:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:03:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:04:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:05:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:06:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:07:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:08:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:09:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:10:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:11:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:12:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:13:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:14:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:15:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:16:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:17:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:18:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:19:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:20:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:21:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:22:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:23:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:24:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:25:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:26:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:27:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:28:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:29:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:30:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:31:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:32:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:33:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:34:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:35:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:36:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:37:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:38:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:39:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:40:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:41:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:42:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:43:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:44:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:45:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:46:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:47:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:48:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:49:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:50:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:51:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:52:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:53:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:54:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:55:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:56:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:57:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:58:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T18:59:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:00:00.000+0000"),
                            "level": 10.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T19:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T20:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:57:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:58:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T21:59:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:00:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:01:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:02:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:03:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:04:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:05:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:06:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:07:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:08:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:09:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:10:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:11:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:12:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:13:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:14:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:15:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:16:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:17:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:18:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:19:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:20:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:21:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:22:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:23:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:24:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:25:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:26:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:27:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:28:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:29:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:30:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:31:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:32:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:33:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:34:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:35:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:36:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:37:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:38:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:39:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:40:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:41:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:42:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:43:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:44:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:45:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:46:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:47:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:48:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:49:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:50:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:51:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:52:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:53:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:54:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:55:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:56:00.000+0000"),
                            "level": 0.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:57:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:58:00.000+0000"),
                            "level": 1.8,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T22:59:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:00:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:01:00.000+0000"),
                            "level": 3.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:02:00.000+0000"),
                            "level": 4.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:03:00.000+0000"),
                            "level": 3.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:04:00.000+0000"),
                            "level": 1.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:05:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:06:00.000+0000"),
                            "level": 1.7,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:07:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:08:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:09:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:10:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:11:00.000+0000"),
                            "level": 1.6,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:12:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:13:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:14:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:15:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:16:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:17:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:18:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:19:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:20:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:21:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:22:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:23:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:24:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:25:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:26:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:27:00.000+0000"),
                            "level": 1.4,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:28:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:29:00.000+0000"),
                            "level": 1.3,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:30:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:31:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:32:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:33:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:36:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:37:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:38:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:40:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:42:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:43:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:47:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:48:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:50:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:52:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-11T23:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:00:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:02:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:04:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:05:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:08:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:09:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:11:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:12:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:13:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:14:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:15:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:16:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:19:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:21:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:23:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:29:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:30:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:31:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:36:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:37:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:38:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:40:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:42:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:47:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:50:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T00:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:00:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:01:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:02:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:04:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:05:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:08:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:09:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:11:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:12:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:13:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:14:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:15:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:16:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:19:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:21:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:23:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:29:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:30:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:31:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:36:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:37:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:38:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:40:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:42:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:47:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:50:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:58:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T01:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:00:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:01:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:02:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:04:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:05:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:08:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:09:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:11:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:12:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:13:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:14:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:15:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:16:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:19:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:21:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:23:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:29:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:30:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:31:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:36:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:37:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:38:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:40:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:42:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:46:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:47:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:50:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:52:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:53:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:54:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:56:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T02:59:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:00:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:01:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:02:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:03:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:04:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:05:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:06:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:07:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:08:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:09:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:10:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:11:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:12:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:13:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:14:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:15:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:16:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:17:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:18:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:19:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:20:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:21:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:22:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:23:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:24:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:25:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:26:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:27:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:28:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:29:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:30:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:31:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:32:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:33:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:34:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:35:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:36:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:37:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:38:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:39:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:40:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:41:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:42:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:43:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:44:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:45:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:46:00.000+0000"),
                            "level": 1.1,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:47:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:48:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:49:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:50:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:51:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:52:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:53:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:54:00.000+0000"),
                            "level": 1.0,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:55:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:56:00.000+0000"),
                            "level": 1.2,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:57:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:58:00.000+0000"),
                            "level": 0.9,
                        },
                        {
                            "timestamp": parser.parse("2023-09-12T03:59:00.000+0000"),
                            "level": 0.9,
                        },
                    ],
                    "num_inactive_minutes": 2,
                    "num_moderate_intensity_minutes": 20,
                    "num_high_intensity_minutes": 791,
                    "avg_level": 1.75,
                    "num_low_intensity_minutes": 66,
                },
                "device_data": {
                    "other_devices": [],
                    "activation_timestamp": None,
                    "hardware_version": None,
                    "serial_number": None,
                    "manufacturer": None,
                    "name": None,
                    "software_version": None,
                    "data_provided": [],
                },
                "calories_data": {
                    "net_activity_calories": 746,
                    "total_burned_calories": 2125,
                    "BMR_calories": None,
                    "net_intake_calories": None,
                    "calorie_samples": [],
                },
                "stress_data": {
                    "medium_stress_duration_seconds": None,
                    "rest_stress_duration_seconds": None,
                    "avg_stress_level": None,
                    "stress_duration_seconds": None,
                    "max_stress_level": None,
                    "high_stress_duration_seconds": None,
                    "activity_stress_duration_seconds": None,
                    "low_stress_duration_seconds": None,
                    "samples": [],
                },
                "scores": {"activity": 90, "recovery": 85, "sleep": 78},
                "oxygen_data": {
                    "saturation_samples": [],
                    "vo2_samples": [],
                    "avg_saturation_percentage": None,
                    "vo2max_ml_per_min_per_kg": None,
                },
                "tag_data": {"tags": []},
                "distance_data": {
                    "elevation": {
                        "gain_actual_meters": None,
                        "gain_planned_meters": None,
                        "min_meters": None,
                        "max_meters": None,
                        "avg_meters": None,
                        "loss_actual_meters": None,
                    },
                    "floors_climbed": None,
                    "detailed": {
                        "floors_climbed_samples": [],
                        "step_samples": [],
                        "distance_samples": [],
                        "elevation_samples": [],
                    },
                    "distance_meters": 17589,
                    "swimming": {
                        "pool_length_meters": None,
                        "num_laps": None,
                        "num_strokes": None,
                    },
                    "steps": 2219,
                },
                "heart_rate_data": {
                    "detailed": {
                        "hrv_samples_sdnn": [],
                        "hr_samples": [],
                        "hrv_samples_rmssd": [],
                    },
                    "summary": {
                        "min_hr_bpm": None,
                        "max_hr_bpm": None,
                        "hr_zone_data": [],
                        "avg_hrv_rmssd": None,
                        "avg_hr_bpm": None,
                        "user_max_hr_bpm": None,
                        "avg_hrv_sdnn": None,
                        "resting_hr_bpm": None,
                    },
                },
            }
        },
    },
]
