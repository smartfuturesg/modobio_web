# --------------------------------------------------------------------
#                     Telehealth Client Queue
# --------------------------------------------------------------------
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
#                     Telehealth Staff Availability
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

# --------------------------------------------------------------------
#                     Telehealth Client Staff Bookings
# --------------------------------------------------------------------

# NOTE: The id delta should be 3
# It works out that: booking_window_id_end_time.end_time - booking_window_id_start_time.start_time = 20 minutes
telehealth_client_staff_bookings_post_1_data = {
  'target_date': '2025-02-07',
  'booking_window_id_start_time': 100,
  'booking_window_id_end_time': 103,
  'status': 'Accepted'
}
telehealth_client_staff_bookings_post_2_data = {
  'target_date': '2025-02-07',
  'booking_window_id_start_time': 95,
  'booking_window_id_end_time': 98,
  'status': 'Accepted'
}
# This should break
telehealth_client_staff_bookings_post_3_data = {
  'target_date': '2025-02-07',
  'booking_window_id_start_time': 95,
  'booking_window_id_end_time': 99,
  'status': 'Accepted'
}
# This should break
telehealth_client_staff_bookings_post_4_data = {
  'target_date': '2025-02-07',
  'booking_window_id_start_time': 97,
  'booking_window_id_end_time': 99,
  'status': 'Accepted'
}
# This should break
telehealth_client_staff_bookings_post_5_data = {
  'target_date': '2025-02-07',
  'booking_window_id_start_time': 80,
  'booking_window_id_end_time': 97,
  'status': 'Accepted'
}
# This should break
telehealth_client_staff_bookings_post_6_data = {
  'target_date': '2025-02-07',
  'booking_window_id_start_time': 90,
  'booking_window_id_end_time': 85,
  'status': 'Accepted'
}

# --------------------------------------------------------------------
#                     Telehealth Booking Details
# --------------------------------------------------------------------
import pathlib
from werkzeug.datastructures import FileStorage

rec_file = pathlib.Path(__file__).parent / 'test_m4a_recording.m4a'
img_file = pathlib.Path(__file__).parent / 'test_img_weirdmole.jpg'
telehealth_post_booking_details = {
  'media': (img_file.as_posix() , open(img_file, mode='rb'), 'image/jpg'), 
  'media': (rec_file.as_posix() , open(rec_file, mode='rb'), 'audio/mp4a-latm'),
  'details': 'Testing booking details'
}

telehealth_put_booking_details = {
  'remove_img_rec':{
    'media': FileStorage(filename=''),
    'details': 'Removed image and recording, kept description',
    'idx': 1
  },
  'swap_img_rec':{
    'media': (img_file.as_posix() , open(img_file, mode='rb'), 'image/jpg'),
    'media':(rec_file.as_posix() , open(rec_file, mode='rb'), 'audio/mp4a-latm'),
    'details': 'Swapped files, recording is image and image is recording.',
    'idx': 1
  },
  'change_text_only':{
    'details': 'Only changed text details',
    'idx': 1
  },
  'nothing_to_change':{

  },
  'empty_booking_details':{
    'media': FileStorage(filename=''),
    'details': '',
    'idx': 1
  }
}