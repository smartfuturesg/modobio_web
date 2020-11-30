# from flask.json import dumps
# from requests.auth import _basic_auth_str

# from odyssey.models.user import User, UserLogin

# def test_get_staff_search(test_client, init_database, staff_auth_header):
#     """
#     GIVEN a api end point for retrieving client info
#     WHEN the '/client/<user_id>' resource  is requested (GET)
#     THEN check the response is valid
#     """
#     # get staff authorization to view client data
#     staff = User.query.filter_by(is_staff=True).first()
#     staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
#     token = staffLogin.get_token()
#     
    
#     # Order of test search:
#     # send staff user_id
#     # firstname
#     # lastname
#     # email
#     # firstname and email
#     # FORCE 404 user_id = 2 

#     # send get request for staff user_id = 1
#     response = test_client.get('/staff/?user_id=1', headers=staff_auth_header)
#     assert response.status_code == 200

#     # send get request for first name (note, the actual first name is testY)
#     response = test_client.get('/staff/?firstname=test', headers=staff_auth_header)
#     assert response.status_code == 200
#     assert response.json[0]['firstname'] == 'testy'
#     assert response.json[0]['lastname'] == 'testerson'
#     assert response.json[0]['email'] == 'staff_member@modobio.com'
#     assert response.json[0]['user_id'] == 1

#     # send get request for last name
#     response = test_client.get('/staff/?lastname=test', headers=staff_auth_header)
#     assert response.json[0]['firstname'] == 'testy'
#     assert response.json[0]['lastname'] == 'testerson'
#     assert response.json[0]['email'] == 'staff_member@modobio.com'
#     assert response.json[0]['user_id'] == 1
    
#     # send get request for email
#     response = test_client.get('/staff/?email=staff_member@modobio.com', headers=staff_auth_header)
#     assert response.json[0]['firstname'] == 'testy'
#     assert response.json[0]['lastname'] == 'testerson'
#     assert response.json[0]['email'] == 'staff_member@modobio.com'
#     assert response.json[0]['user_id'] == 1

#     # send get request for first name (note, the actual first name is testY)
#     response = test_client.get('/staff/?firstname=test&email=staff_member@modobio.com', headers=staff_auth_header)
#     assert response.json[0]['firstname'] == 'testy'
#     assert response.json[0]['lastname'] == 'testerson'
#     assert response.json[0]['email'] == 'staff_member@modobio.com'
#     assert response.json[0]['user_id'] == 1

#     # Expect response to fail because there is only TWO staff in the db
#     response = test_client.get('/staff/?user_id=99', headers=staff_auth_header)
#     assert response.status_code == 404