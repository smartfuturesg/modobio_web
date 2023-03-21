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

test_8100_data_1 = {
    "type": "body",
    "data": [
        {
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
            "glucose_data": {
                "blood_glucose_samples": [],
                "detailed_blood_glucose_samples": [],
                "day_avg_blood_glucose_mg_per_dL": None
            },
            "metadata": {
                "end_time": "2023-03-21T08:39:39.812905+00:00",
                "start_time": "2023-03-21T07:58:39.812905+00:00"
            },
            "heart_data": {
                "pulse_wave_velocity_samples": [],
                "afib_classification_samples": [],
                "heart_rate_data": {
                    "detailed": {
                        "hrv_samples_rmssd": [],
                        "hr_samples": [
                            {
                                "timestamp": "2023-03-21T07:58:39.812905+00:00",
                                "bpm": 89
                            },
                            {
                                "timestamp": "2023-03-21T08:04:39.812905+00:00",
                                "bpm": 140
                            },
                            {
                                "timestamp": "2023-03-21T08:10:39.812905+00:00",
                                "bpm": 166
                            },
                            {
                                "timestamp": "2023-03-21T08:16:39.812905+00:00",
                                "bpm": 131
                            },
                            {
                                "timestamp": "2023-03-21T08:22:39.812905+00:00",
                                "bpm": 153
                            },
                            {
                                "timestamp": "2023-03-21T08:28:39.812905+00:00",
                                "bpm": 91
                            },
                            {
                                "timestamp": "2023-03-21T08:34:39.812905+00:00",
                                "bpm": 68
                            }
                        ],
                        "hrv_samples_sdnn": []
                    },
                    "summary": {
                        "min_hr_bpm": 98.20785666186028,
                        "resting_hr_bpm": None,
                        "avg_hrv_sdnn": None,
                        "avg_hrv_rmssd": None,
                        "hr_zone_data": [],
                        "avg_hr_bpm": 82.30125772522062,
                        "user_max_hr_bpm": None,
                        "max_hr_bpm": 120.47989756477591
                    }
                },
                "ecg_signal": []
            },
            "device_data": {
                "name": None,
                "manufacturer": None,
                "serial_number": None,
                "software_version": None,
                "sensor_state": None,
                "other_devices": [],
                "activation_timestamp": None,
                "hardware_version": None
            },
            "temperature_data": {
                "ambient_temperature_samples": [],
                "body_temperature_samples": [],
                "skin_temperature_samples": []
            },
            "ketone_data": {
                "ketone_samples": []
            },
            "measurements_data": {
                "measurements": [
                    {
                        "water_percentage": None,
                        "weight_kg": 96.80456056768,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T07:58:39.812905+00:00",
                        "muscle_mass_g": None,
                        "BMI": 17.015071901958997,
                        "bodyfat_percentage": 31.986490444288897,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 925
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 99.5111808663138,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T08:04:39.812905+00:00",
                        "muscle_mass_g": None,
                        "BMI": 28.50278736500506,
                        "bodyfat_percentage": 72.97699932372711,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1437
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 49.879315129722784,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T08:10:39.812905+00:00",
                        "muscle_mass_g": None,
                        "BMI": 32.381097193948236,
                        "bodyfat_percentage": 97.34799081777577,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1935
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 93.82598669505421,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T08:16:39.812905+00:00",
                        "muscle_mass_g": None,
                        "BMI": 35.30971266649166,
                        "bodyfat_percentage": 30.405053151723283,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1060
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 87.9080170461342,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T08:22:39.812905+00:00",
                        "muscle_mass_g": None,
                        "BMI": 23.91916138983489,
                        "bodyfat_percentage": 97.09100398087296,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1547
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 73.65946056848898,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T08:28:39.812905+00:00",
                        "muscle_mass_g": None,
                        "BMI": 33.75654030069447,
                        "bodyfat_percentage": 5.350876795431914,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1324
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 79.27949708822597,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T08:34:39.812905+00:00",
                        "muscle_mass_g": None,
                        "BMI": 20.727493476330565,
                        "bodyfat_percentage": 40.672696174499876,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 861
                    }
                ]
            },
            "oxygen_data": {
                "avg_saturation_percentage": None,
                "vo2max_ml_per_min_per_kg": None,
                "vo2_samples": [],
                "saturation_samples": []
            },
            "hydration_data": {
                "hydration_amount_samples": [],
                "day_total_water_consumption_ml": None
            }
        }
    ],
    "user": {
        "reference_id": None,
        "scopes": None,
        "provider": "OMRON",
        "last_webhook_update": None,
        "user_id": "c7d2e590-b68f-4879-9672-0b545a7ed923"
    }
}

test_8100_data_2 = {
    "type": "body",
    "data": [
        {
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
            "glucose_data": {
                "blood_glucose_samples": [],
                "detailed_blood_glucose_samples": [],
                "day_avg_blood_glucose_mg_per_dL": None
            },
            "metadata": {
                "end_time": "2023-03-21T08:14:46.501002+00:00",
                "start_time": "2023-03-21T07:28:46.501002+00:00"
            },
            "heart_data": {
                "pulse_wave_velocity_samples": [],
                "afib_classification_samples": [],
                "heart_rate_data": {
                    "summary": {
                        "min_hr_bpm": 152.87661665106208,
                        "max_hr_bpm": 70.62000365558119,
                        "resting_hr_bpm": None,
                        "avg_hrv_sdnn": None,
                        "avg_hrv_rmssd": None,
                        "hr_zone_data": [],
                        "avg_hr_bpm": 159.72455112897097,
                        "user_max_hr_bpm": None
                    },
                    "detailed": {
                        "hrv_samples_sdnn": [],
                        "hrv_samples_rmssd": [],
                        "hr_samples": [
                            {
                                "timestamp": "2023-03-21T07:28:46.501002+00:00",
                                "bpm": 91
                            },
                            {
                                "timestamp": "2023-03-21T07:40:46.501002+00:00",
                                "bpm": 110
                            },
                            {
                                "timestamp": "2023-03-21T07:52:46.501002+00:00",
                                "bpm": 64
                            },
                            {
                                "timestamp": "2023-03-21T08:04:46.501002+00:00",
                                "bpm": 174
                            }
                        ]
                    }
                },
                "ecg_signal": []
            },
            "device_data": {
                "name": None,
                "manufacturer": None,
                "serial_number": None,
                "software_version": None,
                "sensor_state": None,
                "other_devices": [],
                "activation_timestamp": None,
                "hardware_version": None
            },
            "temperature_data": {
                "ambient_temperature_samples": [],
                "body_temperature_samples": [],
                "skin_temperature_samples": []
            },
            "ketone_data": {
                "ketone_samples": []
            },
            "measurements_data": {
                "measurements": [
                    {
                        "water_percentage": None,
                        "weight_kg": 64.04233896096204,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T07:28:46.501002+00:00",
                        "muscle_mass_g": None,
                        "BMI": 22.83833311229036,
                        "bodyfat_percentage": 47.645758716729894,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1034
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 40.412989230990625,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T07:40:46.501002+00:00",
                        "muscle_mass_g": None,
                        "BMI": 17.880216652518705,
                        "bodyfat_percentage": 32.88997188022862,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 2061
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 42.63938494736104,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T07:52:46.501002+00:00",
                        "muscle_mass_g": None,
                        "BMI": 29.32862715121896,
                        "bodyfat_percentage": 71.49854852507234,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1298
                    },
                    {
                        "water_percentage": None,
                        "weight_kg": 79.04770682785623,
                        "skin_fold_mm": None,
                        "lean_mass_g": None,
                        "estimated_fitness_age": None,
                        "height_cm": None,
                        "insulin_type": None,
                        "bone_mass_g": None,
                        "insulin_units": None,
                        "measurement_time": "2023-03-21T08:04:46.501002+00:00",
                        "muscle_mass_g": None,
                        "BMI": 19.426379715174825,
                        "bodyfat_percentage": 22.431179677704925,
                        "urine_color": None,
                        "BMR": None,
                        "RMR": 1470
                    }
                ]
            },
            "oxygen_data": {
                "avg_saturation_percentage": None,
                "vo2_samples": [],
                "vo2max_ml_per_min_per_kg": None,
                "saturation_samples": []
            },
            "hydration_data": {
                "hydration_amount_samples": [],
                "day_total_water_consumption_ml": None
            }
        }
    ],
    "user": {
        "reference_id": None,
        "scopes": None,
        "provider": "OMRON",
        "last_webhook_update": None,
        "user_id": "c7d2e590-b68f-4879-9672-0b545a7ed923"
    }
}
