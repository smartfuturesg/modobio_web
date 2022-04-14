# -----------------------------------
# Data to generate staff availability
# -----------------------------------
# Staff ID 4
from datetime import datetime, timedelta


telehealth_staff_4_general_availability_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '9:00:00',
    'end_time': '17:00:00'
  },
  {
    'day_of_week': 'Tuesday',
    'start_time': '9:00:00',
    'end_time': '17:00:00'
  },
  {
    'day_of_week': 'Wednesday',
    'start_time': '9:00:00',
    'end_time': '17:00:00'
  },
  {
    'day_of_week': 'Thursday',
    'start_time': '9:00:00',
    'end_time': '17:00:00'
  },
  {
    'day_of_week': 'Friday',
    'start_time': '9:00:00',
    'end_time': '17:00:00'
  }
  ]
}
# Staff ID 6
telehealth_staff_6_general_availability_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [
  {
    'day_of_week': 'Saturday',
    'start_time': '9:00:00',
    'end_time': '17:00:00'
  },
  {
    'day_of_week': 'Sunday',
    'start_time': '9:00:00',
    'end_time': '17:00:00'
  }
  ]
}
# Staff ID 8
telehealth_staff_8_general_availability_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '5:00:00',
    'end_time': '12:00:00'
  },
  {
    'day_of_week': 'Wednesday',
    'start_time': '5:00:00',
    'end_time': '12:00:00'
  },
  {
    'day_of_week': 'Friday',
    'start_time': '5:00:00',
    'end_time': '12:00:00'
  }
  ]
}
# Staff ID 10
telehealth_staff_10_general_availability_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Tuesday',
    'start_time': '7:00:00',
    'end_time': '12:00:00'
  },
  {
    'day_of_week': 'Thursday',
    'start_time': '15:00:00',
    'end_time': '17:00:00'
  },  
  {
    'day_of_week': 'Thursday',
    'start_time': '7:00:00',
    'end_time': '12:00:00'
  },
  {
    'day_of_week': 'Thursday',
    'start_time': '15:00:00',
    'end_time': '17:00:00'
  }  
  ]
}
# Staff ID 12
telehealth_staff_12_general_availability_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [
  {
    'day_of_week': 'Saturday',
    'start_time': '2:00:00',
    'end_time': '5:00:00'
  },
  {
    'day_of_week': 'Saturday',
    'start_time': '7:00:00',
    'end_time': '10:00:00'
  }  
  ]
}
# Staff ID 14
telehealth_staff_14_general_availability_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [
  {
    'day_of_week': 'Tuesday',
    'start_time': '18:00:00',
    'end_time': '21:00:00'
  }
  ]
}

# ---------------------
# client staff bookings
# ---------------------
telehealth_booking_data_1 = {
  'target_date': (datetime.now() + timedelta(days=1)).date().isoformat(),
  'booking_window_id_start_time': 109, #9:00
  'booking_window_id_end_time': 112
}
telehealth_booking_data_2 = {
  'target_date': (datetime.now() + timedelta(days=1)).date().isoformat(),
  'booking_window_id_start_time': 187, #15:30
  'booking_window_id_end_time': 190
}
telehealth_booking_data_3 = {
  'target_date': (datetime.now() + timedelta(days=1)).date().isoformat(),
  'booking_window_id_start_time': 118, #9:45
  'booking_window_id_end_time': 121
}

# ------------
# client queue
# ------------

telehealth_queue_client_3_data = {
  'profession_type': 'medical_doctor',
  'target_date': (datetime.now() + timedelta(days=28)).isoformat(),
  'priority': True,
  'medical_gender': 'np',
  'location_id': 1,
  'payment_method_id': None
}

#-------
# Book meetings within a scanning window for upcoming bookings
#--------

# add a new availability for staff member
telehealth_staff_full_availability = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '00:00:00',
    'end_time': '00:00:00'
  },
  { 
    'day_of_week': 'Tuesday',
    'start_time': '00:00:00',
    'end_time': '00:00:00'
  },
  {
    'day_of_week': 'Wednesday',
    'start_time': '00:00:00',
    'end_time': '00:00:00'
  },  
  {
    'day_of_week': 'Thursday',
    'start_time': '00:00:00',
    'end_time': '00:00:00'
  },
  {
    'day_of_week': 'Friday',
    'start_time': '00:00:00',
    'end_time': '00:00:00'
  }  
  ]
}

payment_method_data = {
  'token': '4111111111111111',
  'cardholder_name': 'Test Tester',
  'expiration': '04/25',
  'is_default':True
}

payment_refund_data = {
  "refund_amount":"50.00",
  "payment_id": 1,
  "refund_reason": "abcdefghijklmnopqrstuvwxyz"
}