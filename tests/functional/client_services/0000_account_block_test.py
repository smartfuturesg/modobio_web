from flask.json import dumps

def test_get_user_info(test_client, client_services):
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['user_id'] == test_client.client_id
    assert response.json['modobio_id'] == test_client.client.modobio_id
    assert response.json['is_client'] == True
    assert response.json['client_account_blocked'] == False
    assert response.json['client_account_blocked_reason'] is None
    assert response.json['is_staff'] == False
    assert response.json['staff_account_blocked'] == False
    assert response.json['staff_account_blocked_reason'] is None

def test_get_user_info_not_client_services(test_client, not_client_services):
    # Fail if not logged in as client services member.
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=not_client_services.auth_header)

    assert response.status_code == 401

    # Same when logged in as client requesting own info.
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 401

def test_block_client_account(test_client, client_services):
    data = {'staff': False, 'reason': 'Testing blocked account.'}

    # Set block
    response = test_client.post(
        f'/client-services/account/{test_client.client_id}/block',
        headers=client_services.auth_header,
        data=dumps(data),
        content_type='application/json')

    assert response.status_code == 201

    # Confirm block
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['client_account_blocked'] == True
    assert response.json['client_account_blocked_reason'] == data['reason']
    # Only client portion blocked
    assert response.json['staff_account_blocked'] == False
    assert response.json['staff_account_blocked_reason'] is None

    # Try to do something as blocked user.
    response = test_client.get(
        f'/client/summary/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 401
    assert response.json['message'].startswith('Your account has been blocked.')

def test_unblock_client_account(test_client, client_services):
    data = {'staff': False}

    # Remove block
    response = test_client.delete(
        f'/client-services/account/{test_client.client_id}/block',
        headers=client_services.auth_header,
        data=dumps(data),
        content_type='application/json')

    assert response.status_code == 201

    # Confirm block removed
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['client_account_blocked'] == False
    assert response.json['client_account_blocked_reason'] is None

    # Try to do something as unblocked user.
    response = test_client.get(
        f'/client/summary/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200
    assert response.json['user_id'] == test_client.client_id

def test_block_staff_account(test_client, client_services, not_client_services):
    data = {'staff': True, 'reason': 'Testing blocked account.'}

    # Set block
    response = test_client.post(
        f'/client-services/account/{not_client_services.user_id}/block',
        headers=client_services.auth_header,
        data=dumps(data),
        content_type='application/json')

    assert response.status_code == 201

    # Confirm block
    response = test_client.get(
        f'/client-services/account/{not_client_services.user_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['staff_account_blocked'] == True
    assert response.json['staff_account_blocked_reason'] == data['reason']
    # Only staff portion blocked
    assert response.json['client_account_blocked'] == False
    assert response.json['client_account_blocked_reason'] is None

    # Try to do something as blocked user.
    response = test_client.get(
        f'/staff/offices/{not_client_services.user_id}/',
        headers=not_client_services.auth_header)

    assert response.status_code == 401
    assert response.json['message'].startswith('Your account has been blocked.')

def test_unblock_staff_account(test_client, client_services, not_client_services):
    data = {'staff': True}

    # Remove block
    response = test_client.delete(
        f'/client-services/account/{not_client_services.user_id}/block',
        headers=client_services.auth_header,
        data=dumps(data),
        content_type='application/json')

    assert response.status_code == 201

    # Confirm block removed
    response = test_client.get(
        f'/client-services/account/{not_client_services.user_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['client_account_blocked'] == False
    assert response.json['client_account_blocked_reason'] is None

    # Try to do something as unblocked user.
    response = test_client.get(
        f'/staff/offices/{not_client_services.user_id}/',
        headers=not_client_services.auth_header)

    assert response.status_code == 200
