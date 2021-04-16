import base64
import pathlib

from flask.json import dumps

from tests.functional.user.data import users_notifications_data

from odyssey import db


def test_email_verification(test_client, init_database, client_auth_header):
        """
        Because of the nature of email verification, all endpoints will be 
        tested within 1 test. The endpoints will be called in this order:

        POST /user/email-verification/<user_id>/
        GET /user/email-verification/<user_id>/
        POST /user/email-verification/<token>/
        GET /user/email-verification/token/<user_id>/
        POST /user/email-verification/<user_id>/
        POST /user/email-verification/code/<user_id>/
        GET /user/email-verification/token/<user_id>/
        """

        #create a new pending email verification
        response = test_client.post('/user/email-verification/1/',
                headers=client_auth_header, 
                content_type='application/json')

        assert response.status_code == 201
        
        token = response.json.get('token')

        #use the token to verify the email
        response = test_client.post('/user/email-verification/token/' + token + '/',
                headers=client_auth_header, 
                content_type='application/json')

        assert response.status_code == 200

        #check that token authorization removed the pending verification
        response = test_client.get('/user/email-verification/1/',
                headers=client_auth_header, 
                content_type='application/json')

        assert response.status_code == 404

        #create another pending verification to test code
        response = test_client.post('/user/email-verification/1/',
                headers=client_auth_header, 
                content_type='application/json')

        assert response.status_code == 201

        code = response.json.get('code')

        #use the code to verify the email
        response = test_client.post('/user/email-verification/code/1/',
                headers=client_auth_header,
                data=dumps({'code': code})
                content_type='application/json')

        assert response.status_code = 200