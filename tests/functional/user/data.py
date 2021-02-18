users_client_new_creation_data = {
    "firstname": "Remote",
    "middlename": "Client",
    "lastname": "Test",
    "email": "test_remote_registration@gmail.com",
    "phone_number": "1111111111",
    "is_staff": False,
    "is_client": True
}

users_new_user_client_data = {
  "user_info": {
    "firstname": "Test",
    "middlename": "User",
    "lastname": "Client",
    "email": "test_this_user_client@modobio.com",
    "phone_number": "1111111121",
    "password": "password",
  },
  "client_info": {
    "guardianname": "guardian 1",
    "guardianrole": "guardian role",
    "street": "3325 S Malibu Dr.",
    "city": "Tempe",
    "state": "AZ",
    "zipcode": "85282",
    "country": "US",
    "preferred": 0,
    "emergency_contact": "Emergency",
    "emergency_phone": "6025555555",
    "healthcare_contact": "United",
    "healthcare_phone": "1800676blue",
    "gender": "m",
    "dob": "1991-10-14",
    "profession": "Chef",
    "receive_docs": True
  }
}

users_client_new_info_data = {
    "user_id": 0,
    "guardianname": "guardian 1",
    "guardianrole": "guardian role",
    "street": "3325 S Malibu Dr.",
    "city": "Tempe",
    "state": "AZ",
    "zipcode": "85282",
    "country": "US",
    "preferred": 0,
    "emergency_contact": "Emergency",
    "emergency_phone": "6025555555",
    "healthcare_contact": "United",
    "healthcare_phone": "1800676blue",
    "gender": "m",
    "dob": "1991-10-14",
    "profession": "Chef",
    "receive_docs": True,
    "primary_pharmacy_name": "pharmCo",
    "primary_pharmacy_address": "123 E Pharm Ave Gilbert AZ 85295"

}

users_new_self_registered_client_data = {
  "email": "self_registered_client@mail.com",
  "password": "password_self_reg",
  "firstname": "Testron",
  "lastname": "McClient",
  "middlename": "Selfreg",
  "phone_number": "1112223333"
}

users_to_delete_data = {
  "client_user": {
    "firstname": "Ron",
    "middlename": "Bilius",
    "lastname": "Wesley",
    "email": "ronwesley@mail.com",
    "password": "password2",
    "phone_number": "1111112222"
  },
  "staff_client_user": {
    "user_info": {
      "firstname": "Hermione",
      "middlename": "Jean",
      "lastname": "Granger",
      "email": "hgranger@mail.com",
      "password": "password3",
      "phone_number": "1111113333"
    },
    "staff_info":{
      "access_roles" : [
            "doctor",
            "staff_admin"]
    }
  }
}

users_staff_member_data = {
    "firstname": "testy",
    "lastname": "testerson",
    "email": "staff_member@modobio.com",
    "phone_number": "1111111113",
    "is_staff": True,
    "is_client": False
}

users_staff_passwords_data = {
  "password" : "gogoleplexitykatcity65",
  "current_password": "password",
  "new_password": "salt1ampintheruffs98"
}

users_subscription_data = {
  "is_staff": False,
  "subscription_type_id": 1,
  "subscription_status": "subscribed"
}


users_notifications_data = {
  'title': "Test2",
  'content': "Longer Test2",
  'action': 'https.test2.com',
  'read': False,
  'deleted': True
}

# For readability
# 1/5/2025
users_queue_client_pool_1_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-01-05T02:00:00.000',
  'priority': False
}
# 3/5/2025
users_queue_client_pool_2_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-03-05T02:00:00.000',
  'priority': False
}
# 2/5/2025
users_queue_client_pool_3_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-02-05T02:00:00.000',
  'priority': False
}
# 1/2/2025
users_queue_client_pool_4_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-01-02T02:00:00.000',
  'priority': False
}
# 4/5/2025
users_queue_client_pool_5_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-04-05T02:00:00.000',
  'priority': False
}
# 2/7/2025
users_queue_client_pool_6_data = {
  'profession_type': 'Medical Doctor',
  'target_date': '2025-02-07T02:00:00.000',
  'priority': True
}
