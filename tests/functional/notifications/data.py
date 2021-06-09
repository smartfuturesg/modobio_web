notification = {
    'title': 'A nice title',
    'content': 'You have Spam!',
    'action': 'https://example.com',
    'read': False,
    'deleted': False,
    'notification_type_id': 1}

notification_type = 'Account Management'

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
            'staff_last_name': 'Sterone'}}}
