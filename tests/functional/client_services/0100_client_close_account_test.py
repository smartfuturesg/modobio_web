# The account closed tests are client_services, because they use the
# client_services fixture to check that the account is indeed closed.

from datetime import datetime, timedelta

import pytest

from tests.utils import login

def test_get_client_account_status(test_client, client_services):
    # Confirm not closed yet.
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['client_account_closed'] is None

def test_close_client_account(test_client, client_services):
    # Close account
    response = test_client.post(
        f'/client/account/close/',
        headers=test_client.client_auth_header)

    assert response.status_code == 201

    # Confirm closed
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['client_account_closed'] is not None

    # Check that account_closed was set to now, within a small window.
    now = datetime.now()
    interval = timedelta(seconds=10)

    closed = datetime.fromisoformat(response.json['client_account_closed'])
    assert now - closed < interval

@pytest.mark.xfail(strict=True, reason='Logging out of the API does not invalidate the current token')
def test_access_client_account_after_close(test_client):
    # Try to do something, this should fail.
    response = test_client.get(
        f'/client/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 401

def test_reopen_client_account(test_client, client_services):
    # Logging in clears account_closed setting.
    test_client.client_auth_header = login(test_client, test_client.client, password='123')

    # Confirm account reopened
    response = test_client.get(
        f'/client-services/account/{test_client.client_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['client_account_closed'] is None

    # Try to do something as client.
    response = test_client.get(
        f'/client/{test_client.client_id}/',
        headers=test_client.client_auth_header)

    assert response.status_code == 200

###################################################################

def test_get_staff_account_status(test_client, client_services, not_client_services):
    # Confirm not closed yet.
    response = test_client.get(
        f'/client-services/account/{not_client_services.user_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['staff_account_closed'] is None

def test_close_staff_account(test_client, client_services, not_client_services):
    # Close account
    response = test_client.post(
        f'/staff/account/{not_client_services.user_id}/close/',
        headers=not_client_services.auth_header)

    assert response.status_code == 201

    # Confirm closed
    response = test_client.get(
        f'/client-services/account/{not_client_services.user_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['staff_account_closed'] is not None

    # Check that account_closed was set to now, within a small window.
    now = datetime.now()
    interval = timedelta(seconds=10)

    closed = datetime.fromisoformat(response.json['staff_account_closed'])
    assert now - closed < interval

@pytest.mark.xfail(strict=True, reason='Logging out of the API does not invalidate the current token')
def test_access_staff_account_after_close(test_client, not_client_services):
    # Try to do something, this should fail.
    response = test_client.get(
        f'/staff/offices/{not_client_services.user_id}/',
        headers=not_client_services.auth_header)

    assert response.status_code == 401

def test_reopen_client_account(test_client, client_services, not_client_services):
    # Logging in clears account_closed setting.
    not_client_services.auth_header = login(test_client, not_client_services, password='123')

    # Confirm account reopened
    response = test_client.get(
        f'/client-services/account/{not_client_services.user_id}/',
        headers=client_services.auth_header)

    assert response.status_code == 200
    assert response.json['staff_account_closed'] is None

    # Try to do something as client.
    response = test_client.get(
        f'/staff/offices/{not_client_services.user_id}/',
        headers=not_client_services.auth_header)

    assert response.status_code == 200
