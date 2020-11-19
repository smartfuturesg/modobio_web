# from flask.json import dumps
# from requests.auth import _basic_auth_str

# from odyssey.models.user import User, UserLogin
# from odyssey.models.client import ClientInfo

# def test_get_client_search(test_client, init_database):
#     """
#     GIVEN a api end point for retrieving client info
#     WHEN the '/client/<client id>' resource  is requested (GET)
#     THEN check the response is valid
#     """
#     # get staff authorization to view client data
#     staff = User.query.filter_by(is_staff=True).first()
#     staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
#     token = staffLogin.get_token()
#     headers = {'Authorization': f'Bearer {token}'}
    
#     # Order of test search:
#     # General empty search
#     # record_locator_id
#     # firstname
#     # lastname
#     # email
#     # firstname and email
 
#     # send get request
#     response = test_client.get('/client/clientsearch/', headers=headers)
#     assert response.status_code == 200

#     client = ClientInfo.query.filter_by(user_id=1).first()
#     queryStr = '/client/clientsearch/?record_locator_id=' + client.record_locator_id

#     response = test_client.get(queryStr, headers=headers)
#     assert response.status_code == 200
#     assert response.json['items'][0]['firstname'] == 'Test'
#     assert response.json['items'][0]['lastname'] == 'Client'
#     assert response.json['items'][0]['email'] == 'test_this_client@gmail.com'
#     assert response.json['items'][0]['record_locator_id'] == client.record_locator_id

#     # send get request for first name (note, the actual first name is testY)
#     response = test_client.get('/client/clientsearch/?firstname=test', headers=headers)
#     assert response.status_code == 200
#     assert response.json['items'][0]['firstname'] == 'Test'
#     assert response.json['items'][0]['lastname'] == 'Client'
#     assert response.json['items'][0]['email'] == 'test_this_client@gmail.com'
#     assert response.json['items'][0]['record_locator_id'] == client.record_locator_id

#     # send get request for last name 
#     response = test_client.get('/client/clientsearch/?lastname=client', headers=headers)
#     assert response.status_code == 200
#     assert response.json['items'][0]['firstname'] == 'Test'
#     assert response.json['items'][0]['lastname'] == 'Client'
#     assert response.json['items'][0]['email'] == 'test_this_client@gmail.com'
#     assert response.json['items'][0]['record_locator_id'] == client.record_locator_id

#     # send get request for email 
#     response = test_client.get('/client/clientsearch/?email=test_this_client@gmail.com', headers=headers)
#     assert response.status_code == 200
#     assert response.json['items'][0]['firstname'] == 'Test'
#     assert response.json['items'][0]['lastname'] == 'Client'
#     assert response.json['items'][0]['email'] == 'test_this_client@gmail.com'
#     assert response.json['items'][0]['record_locator_id'] == client.record_locator_id

#     # send get request for first name 
#     response = test_client.get('/client/clientsearch/?firstname=test&email=test_this_client@gmail.com', headers=headers)
#     assert response.status_code == 200
#     assert response.json['items'][0]['firstname'] == 'Test'
#     assert response.json['items'][0]['lastname'] == 'Client'
#     assert response.json['items'][0]['email'] == 'test_this_client@gmail.com'
#     assert response.json['items'][0]['record_locator_id'] == client.record_locator_id
