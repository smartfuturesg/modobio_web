import base64
import pathlib

from flask.json import dumps

from tests.functional.user.data import users_notifications_data

from odyssey import db

def test_notifications_get(test_client, init_database, staff_auth_header):
        """
        GIVEN a api end point for retrieving a user's notifications
        WHEN the 'GET /user/notifications/{user_id}' resource  is requested 
        THEN check the response is valid
        """

        response = test_client.get('/user/notifications/2/',
                headers=staff_auth_header, 
                content_type='application/json')

        assert response.status_code == 200

def test_notifications_put(test_client, init_database, staff_auth_header):
        """
        GIVEN an api end point for updated a user's notifications
        WHEN the 'PUT /user/notifications/{idx} resource is requested
        THEN check the response in valid
        """

        response = test_client.put('/user/notifications/1/',
                headers=staff_auth_header,
                data=dumps(users_notifications_data),
                content_type='application/json'
                )

        assert response.status_code == 201
        assert response.json.get('action') == "https.test2.com"