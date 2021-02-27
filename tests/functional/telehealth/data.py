# For readability
# 1/5/2025
telehealth_queue_client_pool_1_post_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-01-05T02:00:00.000',
  'priority': False,
  'medical_gender': 'f'
}
# 3/5/2025
telehealth_queue_client_pool_2_post_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-03-05T02:00:00.000',
  'priority': False,
  'medical_gender': 'np'
}
# 2/5/2025
telehealth_queue_client_pool_3_post_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-02-05T02:00:00.000',
  'priority': False,
  'medical_gender': 'f'
}
# 1/2/2025
telehealth_queue_client_pool_4_post_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-01-02T02:00:00.000',
  'priority': False,
  'medical_gender': 'm'
}
# 4/5/2025
telehealth_queue_client_pool_5_post_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-04-05T02:00:00.000',
  'priority': False,
  'medical_gender': 'np'
}
# 2/7/2025
telehealth_queue_client_pool_6_post_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-02-07T02:00:00.000',
  'priority': True,
  'medical_gender': 'm'
}
# 2/5/2025
telehealth_queue_client_pool_7_post_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-02-05T02:00:00.000',
  'priority': True,
  'medical_gender': 'f',
  'duration': 30
}

# --------------------------------------------------------------------

telehealth_staff_general_availability_1_post_data = {
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '11:00:00',
    'end_time': '12:00:00'
  }]
}

telehealth_staff_general_availability_2_post_data = {
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '8:00:00',
    'end_time': '9:00:00'
  },
  {
    'day_of_week': 'Tuesday',
    'start_time': '11:00:00',
    'end_time': '13:00:00'
  },
  {
    'day_of_week': 'Monday',
    'start_time': '13:00:00',
    'end_time': '20:00:00'
  },
  {
    'day_of_week': 'Thursday',
    'start_time': '9:00:00',
    'end_time': '20:00:00'
  },
  {
    'day_of_week': 'Saturday',
    'start_time': '13:00:00',
    'end_time': '20:00:00'
  },
  {
    'day_of_week': 'Friday',
    'start_time': '13:00:00',
    'end_time': '20:00:00'
  },  
  {
    'day_of_week': 'Sunday',
    'start_time': '13:00:00',
    'end_time': '20:00:00'
  }
  ]
}
# Invalid inputs:
telehealth_staff_general_availability_bad_3_post_data = {
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '25:00:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_4_post_data = {
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '10:70:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_5_post_data = {
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '-10:00:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_6_post_data = {
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '10:-10:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_7_post_data = {
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '10:10:00',
    'end_time': '09:00:00'
  }]
}