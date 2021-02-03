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
  "subscription_status": 'subscribed',
  "subscription_type_id": 2
}