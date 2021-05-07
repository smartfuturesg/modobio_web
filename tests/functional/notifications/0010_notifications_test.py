from flask.json import dumps

from .data import notification, notification_type, notification_update

def test_notifications_post(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for creating notifications,
        WHEN the POST /notifications/<user_id>/ resource is requested,
        THEN check that the response is valid.
        """

        response = test_client.post(
            '/notifications/1/',
            headers=client_auth_header,
            data=dumps(notification),
            content_type='application/json')

        assert response.status_code == 201

def test_notifications_get(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for retrieving notifications,
        WHEN the GET /notifications/<user_id>/ resource is requested,
        THEN check that the response is valid.
        """

        response = test_client.get(
            '/notifications/1/',
            headers=client_auth_header,
            content_type='application/json')

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 1

        notif = response.json[0]
        assert notif.get('title') == notification['title']
        assert notif.get('content') == notification['content']
        assert notif.get('action') == notification['action']
        assert notif.get('read') == notification['read']
        assert notif.get('deleted') == notification['deleted']
        assert notif.get('notification_type') == notification_type

def test_notifications_put(test_client, init_database, client_auth_header):
        """
        GIVEN an API endpoint for updating notifications,
        WHEN the PUT /notifications/<user_id>/<notification_id>/ resource is requested,
        THEN check that the response is valid.
        """

        response = test_client.put(
            '/notifications/1/1/',
            headers=client_auth_header,
            data=dumps(notification_update),
            content_type='application/json')

        assert response.status_code == 200

        # No output from PUT, check again.
        response = test_client.get(
            '/notifications/1/',
            headers=client_auth_header, 
            content_type='application/json')

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 1

        notif = response.json[0]
        # Unchanged
        assert notif.get('title') == notification['title']
        assert notif.get('content') == notification['content']
        assert notif.get('action') == notification['action']
        assert notif.get('notification_type') == notification_type

        # CHanged
        assert notif.get('read') == notification_update['read']
        assert notif.get('deleted') == notification_update['deleted']
