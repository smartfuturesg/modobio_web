import pathlib

users_staff_new_user_data = {
  "user_info": {
    "firstname": "Test",
    "middlename": "User",
    "lastname": "Staff",
    "email": "test_this_user_staff@modobio.com",
    "phone_number": "1111111112",
    "password": "password",
    "dob": '1995-6-13',
    "biological_sex_male": True
  },
  "staff_info": {
    "access_roles" : [
            "medical_doctor"
  ]
  }
}

img_file = pathlib.Path(__file__).parent / 'test_profile_picture.png'

staff_profile_data = {
    'change_everything': {
        'firstname': 'Mario',
        'middlename': 'The',
        'lastname': 'Plumber',
        'biological_sex_male': 'True',
        'bio': 'It\'s a me, Mario!',
        'dob': '1995-06-14',
        'profile_picture': (img_file.as_posix(), img_file.name, 'image/png')},
    'change_only_picture': {
        'profile_picture': (img_file.as_posix(), img_file.name, 'image/png')},
    'remove_picture': {
        'profile_picture': (None, 'no name', 'image/png')}}

staff_calendar_events_data = {
  "recurring":{
    "daily_event":{
      "start_date": "2021-05-19",
      "start_time": "13:30:00",
      "end_date": "2021-05-31",
      "end_time": "14:30:00",
      "recurring": True,
      "recurrence_type": "Daily",
      "availability_status": "Busy",
      "location": "officium",
      "description": "Sunt in culpa qui officia deserunt mollit anim id est laborum.",
      "all_day": False
    },
    "weekly_event":{
      "start_date": "2021-07-01",
      "start_time": "00:00",
      "end_time": "00:00",
      "recurring": True,
      "recurrence_type": "Weekly",
      "availability_status": "Busy",
      "location": "officium",
      "description": "Consectetur adipiscing elit.",
      "all_day": True
    },
    "monthly_event":{
      "start_date": "2021-03-31",
      "start_time": "8:30:00",
      "end_date": "2021-12-31",
      "end_time": "10:00:00",
      "recurring": True,
      "recurrence_type": "Monthly",
      "availability_status": "Available",
      "location": "officium",
      "description": "Lorem ipsum dolor sit amet.",
      "all_day": False
    },
    "yearly_event":{
      "start_date": "2020-02-29",
      "start_time": "15:00:00",
      "end_time": "16:00:00",
      "recurring": True,
      "recurrence_type": "Yearly",
      "availability_status": "Busy",
      "location": "officium",
      "description": "Nisi ut aliquid ex ea commodi consequatur?",
      "all_day": False
    },
    "invalid_event":{
      "start_date": "2020-02-29",
      "start_time": "15:00:00",
      "end_time": "16:00:00",
      "recurring": True,
      "availability_status": "Busy",
      "location": "officium",
      "description": "Nisi ut aliquid ex ea commodi consequatur?",
      "all_day": False
    }
  },
  "non-recurring":{
    "valid_event":{
      "start_date": "2021-05-19",
      "start_time": "13:30:00",
      "end_date": "2021-05-20",
      "end_time": "14:30:00",
      "recurring": False,
      "availability_status": "Busy",
      "location": "officium",
      "description": "Sunt in culpa qui officia deserunt mollit anim id est laborum.",
      "all_day": True
    },
    "invalid_event":{
      "start_date": "2021-02-29",
      "start_time": "13:30:00",
      "end_date": "2021-02-29",
      "end_time": "14:30:00",
      "recurring": False,
      "availability_status": "Busy",
      "location": "officium",
      "description": "Sunt in culpa qui officia deserunt mollit anim id est laborum.",
      "all_day": False
    }
  },
  "edit_event":{
    "previous_start_date": "2021-05-30",
    "entire_series": True,
    "event_to_update_idx": 1,
    "revised_event_schema": {
      "start_date": "2021-05-19",
      "start_time": "9:00",
      "end_date": "2021-12-31",
      "end_time": "10:30",
      "recurring": True,
      "recurrence_type": "Weekly",
      "availability_status": "Busy",
      "location": "officium",
      "description": "Sunt in culpa qui officia.",
      "all_day": False
    }
  }
}

staff_office_data = {
  "normal_data": {
    "city": "Miami",
    "phone_type": "primary",
    "territory_id": 1,
    "zipcode": "85260",
    "email": "string@modobio.com",
    "phone": "4804389574",
    "street": "123 Test St.",
    "fax": "4804389574"
  },
  "normal_data_2": {
    "city": "Tampa",
    "phone_type": "home",
    "territory_id": 1,
    "zipcode": "85641",
    "email": "string@modobio.com",
    "phone": "4804389575",
    "street": "123 Place St.",
    "fax": "4804389575"
  },
  "invalid_territory_id": {
    "city": "Miami",
    "phone_type": "primary",
    "territory_id": 999,
    "zipcode": "85260",
    "email": "string@modobio.com",
    "phone": "1234567",
    "street": "123 Test St.",
    "fax": "1234568"
  },
  "too_long": {
    "city": "Miami",
    "phone_type": "primary",
    "territory_id": 1,
    "zipcode": "85260",
    "email": "string@modobio.com",
    "phone": "111111111111111111111",
    "street": "123 Test St.",
    "fax": "1234568"
  },
  "invalid_phone_type": {
    "city": "Miami",
    "phone_type": "invalid",
    "territory_id": 1,
    "zipcode": "85260",
    "email": "string@modobio.com",
    "phone": "1234567",
    "street": "123 Test St.",
    "fax": "1234568"
  }
}