import pathlib
import time 

from flask.json import dumps

from odyssey.models.user import User, UserLogin
from odyssey.models.client import ClientConsultContract, ClientPolicies ,ClientSubscriptionContract
from tests.data.clients.clients_data import (
    clients_policies_data,
    clients_consult_data,
    clients_subscription_data
)

def test_post_subscription_contract(test_client, init_database):
    """
    GIVEN a api end point for signing a contract
    WHEN the '/client/subscriptioncontract/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = {"signdate" : clients_subscription_data["signdate"], "signature": clients_subscription_data["signature"]}
    # send get request for client info on user_id = 1 
    response = test_client.post('/client/subscriptioncontract/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    #wait for pdf generation
    time.sleep(3)
    client_subscription = ClientSubscriptionContract.query.filter_by(user_id=1).order_by(ClientSubscriptionContract.signdate.desc()).first()
    assert response.status_code == 201
    assert client_subscription.signdate.strftime("%Y-%m-%d") == clients_subscription_data["signdate"]
    assert client_subscription.pdf_path
    assert pathlib.Path(client_subscription.pdf_path).exists()

def test_get_subscription_contract(test_client, init_database):
    """
    GIVEN a api end point for retrieving the most recent contract
    WHEN the '/client/subscriptioncontract/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/subscriptioncontract/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json["signdate"] == clients_subscription_data["signdate"]
    

def test_post_consult_contract(test_client, init_database):
    """
    GIVEN a api end point for signing a contract
    WHEN the '/client/consultcontract/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = {"signdate" : clients_consult_data["signdate"], "signature": clients_consult_data["signature"]}
    # send get request for client info on user_id = 1 
    response = test_client.post('/client/consultcontract/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    #wait for pdf generation
    time.sleep(3)
    client_consult = ClientConsultContract.query.filter_by(user_id=1).order_by(ClientConsultContract.signdate.desc()).first()
    assert response.status_code == 201
    assert client_consult.signdate.strftime("%Y-%m-%d") == clients_consult_data["signdate"]
    assert client_consult.pdf_path
    assert pathlib.Path(client_consult.pdf_path).exists()

def test_get_consult_contract(test_client, init_database):
    """
    GIVEN a api end point for retrieving the most recent contract
    WHEN the '/client/consultcontract/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/consultcontract/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json["signdate"] == clients_consult_data["signdate"]


def test_post_policies_contract(test_client, init_database):
    """
    GIVEN a api end point for signing a contract
    WHEN the '/client/policies/<client id>' resource  is requested (POST)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    payload = {"signdate" : clients_policies_data["signdate"], "signature": clients_policies_data["signature"]}
    # send get request for client info on user_id = 1 
    response = test_client.post('/client/policies/1/',
                                headers=headers, 
                                data=dumps(payload), 
                                content_type='application/json')
    #wait for pdf generation
    time.sleep(3)
    client_policies = ClientPolicies.query.filter_by(user_id=1).order_by(ClientPolicies.signdate.desc()).first()
    assert response.status_code == 201
    assert client_policies.signdate.strftime("%Y-%m-%d") == clients_policies_data["signdate"]
    assert client_policies.pdf_path
    assert pathlib.Path(client_policies.pdf_path).exists()

def test_get_policies_contract(test_client, init_database):
    """
    GIVEN a api end point for retrieving the most recent contract
    WHEN the '/client/policies/<client id>' resource  is requested (GET)
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    staffLogin = UserLogin.query.filter_by(user_id=staff.user_id).one_or_none()
    token = staffLogin.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    # send get request for client info on user_id = 1 
    response = test_client.get('/client/policies/1/',
                                headers=headers, 
                                content_type='application/json')
                                
    assert response.status_code == 200
    assert response.json["signdate"] == clients_policies_data["signdate"]
