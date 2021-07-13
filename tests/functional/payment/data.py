payment_methods_data = {
    'normal_data': {
        'token': '4111111111111111',
        'expiration': '04/25',
        'is_default': True
    },
    'normal_data_2': {
        'token': '5500000000000004',
        'expiration': '04/25',
        'is_default': True
    },
    'normal_data_3': {
        'token': '6011000000000004',
        'expiration': '04/25',
        'is_default': False
    },
    'invalid_card': {
        'token': '9999999999999999',
        'expiration': '04/25',
        'is_default': True
    },
    'expired': {
        'token': '4111111111111111',
        'expiration': '01/20',
        'is_default': False
    }
}

payment_status_auth_header = {
    'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0dHlwZSI6Im9yZ2FuaXphdGlvbiIsIm9uYW1lIjoiSW5zdGFNZWQifQ.BGQgeZ_vAO40S1rjDusPCu1DAGryyBulm1i72E9ze4Q'
}

payment_status_data = {
    'invalid_user_id': {
        "user_id": 99,
        "original_transaction_status_code": "C",
        "card_present_status": "NotPresentInternet",
        "transaction_action": "Sale",
        "save_on_file_transaction_id": "BASJDNFSA76YASD",
        "original_transaction_id": "HASDYF7SDFYAF",
        "payment_transaction_id": "SDFHUASDF67IA",
        "request_amount": "10.99",
        "current_transaction_status_code": "C"
    },
    'valid_data': {
        "user_id": 1,
        "original_transaction_status_code": "C",
        "card_present_status": "NotPresentInternet",
        "transaction_action": "Sale",
        "save_on_file_transaction_id": "BASJDNFSA76YASD",
        "original_transaction_id": "HASDYF7SDFYAF",
        "payment_transaction_id": "SDFHUASDF67IA",
        "request_amount": "10.99",
        "current_transaction_status_code": "C"
    }
}