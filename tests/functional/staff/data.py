import pathlib

users_staff_new_user_data = {
  "user_info": {
    "firstname": "Test",
    "middlename": "User",
    "lastname": "Staff",
    "email": "test_this_user_staff@modobio.com",
    "phone_number": "1111111112",
    "password": "password"
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
        'profile_picture': (img_file.as_posix(), 'image/png')},
    'change_only_picture': {
        'profile_picture': (img_file.as_posix(), 'image/png')},
    'remove_picture': {
        'profile_picture': None}}
