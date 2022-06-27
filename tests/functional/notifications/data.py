notification_type = 'Account'

notification_update = {
    'read': True,
    'deleted': True,
    'notification_type_id': 1}

device = {
    'device_id': 'abc',
    'device_token': '123',
    'device_voip_token': '456',
    'device_description': 'macOS/11.3',
    'device_platform': 'apple'}

alert = {
    'content': {
        'aps': {
            'alert': {
                'title': 'Test',
                'body': 'Test message 👍.'}}}}

voip = {
    'content': {
        'aps': {},
        'type': 'incoming-call',
        'data': {
            'booking_id': 1,
            'booking_description': 'Test booking',
            'staff_id': 2,
            'staff_first_name': 'Test',
            'staff_middle_name': 'O.',
            'staff_last_name': 'Sterone',
            'staff_profile_picture': {} ,
            'booking_uid': 'f20ef9bc-c6ea-477e-ae95-13ef845489e2'}}}
