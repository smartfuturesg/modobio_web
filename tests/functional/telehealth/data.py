import pathlib
# TODO update dates to current year + 1 to ensure the tests always use a future date
from datetime import timedelta, datetime

from odyssey.utils.constants import DAY_OF_WEEK

today = datetime.utcnow().weekday()
days_til_monday = timedelta(weeks= 2, days= -today + DAY_OF_WEEK.index('Monday'))
target_date_next_monday = datetime.utcnow() + days_til_monday

now = datetime.now()
# For readability
# 1/5/2025
# Sunday
telehealth_queue_client_pool_1_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': (now + timedelta(weeks=1)).isoformat(),
  'priority': False,
  'medical_gender': 'f',
  'payment_method_id': None,
  'location_id': 1
}
# 3/3/2025
# Monday
telehealth_queue_client_pool_2_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': (now + timedelta(weeks=2)).isoformat(),
  'priority': False,
  'medical_gender': 'np',
  'payment_method_id': None,
  'location_id': 1
}
# 2/5/2025
# Wednesday
telehealth_queue_client_pool_3_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': (now + timedelta(weeks=3)).isoformat(),
  'priority': False,
  'medical_gender': 'f',
  'payment_method_id': None,
  'location_id': 1
}
# 1/2/2025
# Thursday
telehealth_queue_client_pool_4_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': (now + timedelta(weeks=4)).isoformat(),
  'priority': False,
  'medical_gender': 'm',
  'payment_method_id': None,
  'location_id': 1
}
# 4/5/2025
# Friday
telehealth_queue_client_pool_5_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': (now + timedelta(weeks=5)).isoformat(),
  'priority': False,
  'medical_gender': 'np',
  'payment_method_id': None,
  'location_id': 1
}
# 2/7/2025
# Friday
telehealth_queue_client_pool_6_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': (now + timedelta(weeks=6)).isoformat(),
  'priority': True,
  'medical_gender': 'm',
  'payment_method_id': None,
  'location_id': 1
}
# Same date as telehealth_queue_client_pool_3_post_data
telehealth_queue_client_pool_7_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': (now + timedelta(weeks=3)).isoformat(),
  'priority': True,
  'medical_gender': 'f',
  'duration': 30,
  'payment_method_id': None,
  'location_id': 1
}

telehealth_queue_client_pool_8_post_data = {
  'profession_type': 'medical_doctor',
  'target_date': str(target_date_next_monday),
  'priority': False,
  'medical_gender': 'np',
  'payment_method_id': None,
  'location_id': 1,
  'duration':30,
  'timezone': 'UTC'
}

# --------------------------------------------------------------------
#                     Telehealth Staff Availability
# --------------------------------------------------------------------
telehealth_staff_general_availability_1_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '11:00:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_3_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '00:00:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_2_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
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
    'day_of_week': 'Wednesday',
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
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '25:00:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_4_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '10:70:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_5_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '-10:00:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_6_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '10:-10:00',
    'end_time': '12:00:00'
  }]
}
telehealth_staff_general_availability_bad_7_post_data = {
  'settings': {
    'timezone': 'UTC',
    'auto_confirm': True
  },
  'availability': [{
    'day_of_week': 'Monday',
    'start_time': '10:10:00',
    'end_time': '09:00:00'
  }]
}
# NOTE: The id delta should be 3
# It works out that: booking_window_id_end_time.end_time - booking_window_id_start_time.start_time = 20 minutes
# NOTE: This works when there is no buffer
telehealth_client_staff_bookings_post_1_data = {
  'target_date': str(target_date_next_monday.date()),
  'booking_window_id_start_time': 100,
  'booking_window_id_end_time': 103
}

telehealth_client_staff_bookings_post_2_data = {
  'target_date': (target_date_next_monday + timedelta(weeks=1)).date().isoformat(),
  'booking_window_id_start_time': 157,
  'booking_window_id_end_time': 160
}
#client already has appointment at this time
telehealth_client_staff_bookings_post_3_data = {
  'target_date': (target_date_next_monday + timedelta(weeks=1)).date().isoformat(),
  'booking_window_id_start_time': 157,
  'booking_window_id_end_time': 160
}
# This should break
telehealth_client_staff_bookings_post_4_data = {
  'target_date': (target_date_next_monday + timedelta(weeks=1)).date().isoformat(),
  'booking_window_id_start_time': 105,
  'booking_window_id_end_time': 107
}
# This should break
telehealth_client_staff_bookings_post_5_data = {
  'target_date': (target_date_next_monday + timedelta(weeks=1)).date().isoformat(),
  'booking_window_id_start_time': 80,
  'booking_window_id_end_time': 97
}
# This should break
telehealth_client_staff_bookings_post_6_data = {
  'target_date': (target_date_next_monday + timedelta(weeks=1)).date().isoformat(),
  'booking_window_id_start_time': 90,
  'booking_window_id_end_time': 85
}

telehealth_client_staff_bookings_put_1_data = {
  'status': 'Canceled'
}

# --------------------------------------------------------------------
#                     Telehealth Booking Details
# --------------------------------------------------------------------

rec_file = pathlib.Path(__file__).parent / 'test_m4a_recording.m4a'
img_file = pathlib.Path(__file__).parent / 'test_img_weirdmole.jpg'
telehealth_post_booking_details = {
    'images': (img_file.as_posix(), img_file.name, 'image/jpeg'),
    'voice': (rec_file.as_posix(), rec_file.name, 'audio/mp4'),
    'details': 'Testing booking details'}

telehealth_put_booking_details = {
    'remove_img_rec': {
        'images': None,
        'voice': None,
        'details': 'Removed image and recording, kept description'},
    'swap_img_rec': {
        'images': (img_file.as_posix(), img_file.name, 'image/jpeg'),
        'voice': (rec_file.as_posix(), rec_file.name, 'audio/mp4'),
        'details': 'Swapped files, recording is image and image is recording.'},
    'change_text_only': {
        'details': 'Only changed text details'},
    'nothing_to_change': {},
    'empty_booking_details': {
        'images': None,
        'voice': None,
        'details': ''}}

telehealth_exceptions_post_data = {
  "bad_data_1":
    [
      {
      "exception_date": "2022-09-20",
      "exception_booking_window_id_end_time": 100,
      "exception_booking_window_id_start_time": 120,
      "is_busy": True,
      "label": "end time before start time"
      }
    ],
  "bad_data_2": 
    [
        {
      "exception_date": "2030-01-01",
      "exception_booking_window_id_end_time": 150,
      "exception_booking_window_id_start_time": 120,
      "is_busy": True,
      "label": "end date too far in the future"
      }
    ],
  "good_data":
    [
      {
      "exception_date": "2022-09-20",
      "exception_booking_window_id_end_time": 150,
      "exception_booking_window_id_start_time": 120,
      "is_busy": True,
      "label": "test good data"
      }
  ]
}