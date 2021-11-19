from flask.json import dumps

from odyssey.api.client.models import ClientMobileSettings, ClientNotificationSettings

from tests.functional.client.data import clients_mobile_settings

def test_post_client_mobile_settings(test_client):
    # Test regular
    response = test_client.post(
        f'/client/mobile-settings/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(clients_mobile_settings),
        content_type='application/json')

    assert response.status_code == 201

    # Double POST should fail
    response = test_client.post(
        f'/client/mobile-settings/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(clients_mobile_settings),
        content_type='application/json')

    assert response.status_code == 400

    # Remove data to continue testing POST
    settings = (
        test_client.db.session
        .query(ClientMobileSettings)
        .filter_by(user_id=test_client.client_id)
        .one_or_none())

    notifications = (
        test_client.db.session
        .query(ClientNotificationSettings)
        .filter_by(user_id=test_client.client_id)
        .all())

    test_client.db.session.delete(settings)
    for notif in notifications:
        test_client.db.session.delete(notif)
    test_client.db.session.commit()

    # Test invalid notification type
    data = clients_mobile_settings.copy()
    data['notification_type_ids'] = [1, 9999]

    response = test_client.post(
        f'/client/mobile-settings/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(data),
        content_type='application/json')

    assert response.status_code == 400

    # TODO: deprecated
    # Test old push_notification_type_ids
    data = clients_mobile_settings.copy()
    data.pop('notification_type_ids')

    response = test_client.post(
        f'/client/mobile-settings/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_client_mobile_settings(test_client):
    response = test_client.get(
        f'/client/mobile-settings/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert (response.json['general_settings']['date_format'] ==
            clients_mobile_settings['general_settings']['date_format'])
    assert (response.json['notification_type_ids'] == 
            clients_mobile_settings['notification_type_ids'])

def test_put_client_mobile_settings(test_client):
    # Update settings
    data = clients_mobile_settings.copy()
    data['general_settings']['is_right_handed'] = False
    data['notification_type_ids'] = [1, 3, 9]

    response = test_client.put(
        f'/client/mobile-settings/{test_client.client_id}/',
        data=dumps(data),
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 201

    response = test_client.get(
        f'/client/mobile-settings/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['general_settings']['is_right_handed'] == False
    assert response.json['notification_type_ids'] == [1, 3, 9]

    # Update settings old push_notification_type_ids
    # TODO: deprecated
    push_ids = [
        {'notification_type_id': 2},
        {'notification_type_id': 4}]
    data.pop('notification_type_ids')
    data['push_notification_type_ids'] = push_ids

    response = test_client.put(
        f'/client/mobile-settings/{test_client.client_id}/',
        data=dumps(data),
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 201

    response = test_client.get(
        f'/client/mobile-settings/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['notification_type_ids'] == [2, 4]
    # Round-trip adds user_id
    for p in push_ids:
        p['user_id'] = test_client.client_id
    assert response.json['push_notification_type_ids'] == push_ids

    # Invalid date format should fail
    clients_mobile_settings['general_settings']['date_format'] = 'notadateformat'

    response = test_client.put(
        f'/client/mobile-settings/{test_client.client_id}/',
        data=dumps(clients_mobile_settings),
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 400
