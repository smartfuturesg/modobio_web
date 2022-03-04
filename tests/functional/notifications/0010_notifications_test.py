from flask.json import dumps

from odyssey.api.notifications.models import Notifications

from .data import notification, notification_type, notification_update

def test_notifications_post(test_client):
        response = test_client.post(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            data=dumps(notification),
            content_type='application/json')

        assert response.status_code == 201

def test_notifications_get(test_client):
        response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 1

        notif = response.json[0]
        assert notif.get('title') == notification['title']
        assert notif.get('content') == notification['content']
        assert notif.get('read') == notification['read']
        assert notif.get('deleted') == notification['deleted']
        assert notif.get('notification_type') == notification_type

def test_notifications_put(test_client):
        _notification = Notifications.query.filter_by(user_id = test_client.client_id).first()
        response = test_client.put(
            f'/notifications/{test_client.client_id}/{_notification.notification_id}/',
            headers=test_client.client_auth_header,
            data=dumps(notification_update),
            content_type='application/json')

        assert response.status_code == 200

        # No output from PUT, check again.
        response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 1

        notif = response.json[0]
        # Unchanged
        assert notif.get('title') == notification['title']
        assert notif.get('content') == notification['content']
        assert notif.get('notification_type') == notification_type

        # CHanged
        assert notif.get('read') == notification_update['read']
        assert notif.get('deleted') == notification_update['deleted']
