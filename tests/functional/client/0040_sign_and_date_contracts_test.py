import pathlib
import time

from flask.json import dumps

from odyssey.api.user.models import User, UserLogin
from odyssey.api.client.models import (
    ClientConsultContract,
    ClientPolicies,
    ClientSubscriptionContract)

from .data import (
    clients_policies_data,
    clients_consult_data,
    clients_subscription_data)

def test_post_subscription_contract(test_client):
    payload = {
        'signdate' : clients_subscription_data['signdate'],
        'signature': clients_subscription_data['signature']}

    response = test_client.post(
        f'/client/subscriptioncontract/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    #wait for pdf generation
    time.sleep(6)
    client_subscription = (
        ClientSubscriptionContract
        .query
        .filter_by(user_id=test_client.client_id)
        .order_by(
            ClientSubscriptionContract
            .signdate
            .desc())
        .first())

    assert response.status_code == 201
    assert client_subscription.signdate.strftime('%Y-%m-%d') == clients_subscription_data['signdate']
    assert client_subscription.pdf_path

def test_get_subscription_contract(test_client):
    response = test_client.get(
        f'/client/subscriptioncontract/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['signdate'] == clients_subscription_data['signdate']

def test_post_consult_contract(test_client):
    payload = {
        'signdate' : clients_consult_data['signdate'],
        'signature': clients_consult_data['signature']}

    response = test_client.post(
        f'/client/consultcontract/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    #wait for pdf generation
    time.sleep(3)
    client_consult = (
        ClientConsultContract
        .query
        .filter_by(user_id=test_client.client_id)
        .order_by(
            ClientConsultContract
            .signdate
            .desc())
        .first())

    assert response.status_code == 201
    assert client_consult.signdate.strftime('%Y-%m-%d') == clients_consult_data['signdate']
    assert client_consult.pdf_path

def test_get_consult_contract(test_client):
    response = test_client.get(
        f'/client/consultcontract/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['signdate'] == clients_consult_data['signdate']

def test_post_policies_contract(test_client):
    payload = {
        'signdate': clients_policies_data['signdate'],
        'signature': clients_policies_data['signature']}

    response = test_client.post(
        f'/client/policies/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payload),
        content_type='application/json')

    #wait for pdf generation
    time.sleep(3)
    client_policies = (
        ClientPolicies
        .query
        .filter_by(user_id=test_client.client_id)
        .order_by(
            ClientPolicies
            .signdate
            .desc())
        .first())

    assert response.status_code == 201
    assert client_policies.signdate.strftime('%Y-%m-%d') == clients_policies_data['signdate']
    assert client_policies.pdf_path

def test_get_policies_contract(test_client):
    response = test_client.get(
        f'/client/policies/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['signdate'] == clients_policies_data['signdate']
