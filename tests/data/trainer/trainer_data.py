trainer_moxy_assessment_data = {
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

trainer_heart_assessment_data = {
  "co2_tolerance": 60,
  "resting_hr": 55,
  "estimated_vo2_max": 84,
  "notes": "some noty notes",
  "max_hr": 200,
  "theoretical_max_hr": 209,
  "avg_training_hr": 145,
  "avg_eval_hr": 110
}

trainer_strength_assessment_data = {
  "user_id": 0,
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

trainer_power_assessment_data = {
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

trainer_movement_assessment_data = {
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

trainer_chessboard_assessment_data = {
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

trainer_lung_assessment_data = {
  "breaths_per_minute": 67,
  "max_minute_volume": 409,
  "notes": "little struggle but overall fine",
  "liters_min_kg": 74,
  "bag_size": 6,
  "duration": 150
}

trainer_moxy_rip_data = {
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


trainer_medical_physical_data = {
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

trainer_fitness_questionnaire_data = {
  "sleep_hours": "6-8",
  "energy_level": 5,
  "libido_level": 2,
  "stress_level": 4,
  "stress_sources": [
    "Family",
    "Finances",
    "Social Obligations"
  ],
  "trainer_expectations": ["Expertise"],
  "current_fitness_level": 6,
  "lifestyle_goals": [
    "Increased Energy"
  ],
  "physical_goals": [
    "Weight Loss",
    "Increase Strength"
  ],
  "sleep_quality_level": 2,
  "goal_fitness_level": 9
}
