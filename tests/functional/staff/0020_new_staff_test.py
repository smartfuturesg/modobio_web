import base64
import random

import pytest

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.lookup.models import LookupTerritoriesOfOperations
from odyssey.api.user.models import User, UserPendingEmailVerifications, UserTokenHistory
from odyssey.api.staff.models import StaffOperationalTerritories, StaffRoles
from odyssey.utils.constants import STAFF_ROLES
from .data import users_staff_new_user_data

@pytest.fixture(scope='module')
def new_staff(test_client):
    response = test_client.post(
        '/user/staff/',
        headers=test_client.staff_auth_header,
        data=dumps(users_staff_new_user_data),
        content_type='application/json')

    assert response.status_code == 201

    return response.json['user_info']

@pytest.fixture(scope='module')
def new_staff_header(test_client, new_staff):
    uid = new_staff['user_id']
    email = users_staff_new_user_data['user_info']['email']
    passw = users_staff_new_user_data['user_info']['password']
    creds = base64.b64encode(f'{email}:{passw}'.encode('utf-8')).decode('utf-8')

    headers = {'Authorization': f'Basic {creds}'}
    response = test_client.post(
        '/staff/token/',
        headers=headers,
        content_type='application/json')

    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

def test_creating_new_staff(test_client, new_staff):
    # some simple checks for validity

    assert new_staff['firstname'] == users_staff_new_user_data['user_info']['firstname']
    assert new_staff['is_staff'] == True
    assert new_staff['is_client'] == False
    assert new_staff['email_verified'] == False

    # Register the staff's email address (code)
    verification = (
        UserPendingEmailVerifications
        .query
        .filter_by(user_id=new_staff['user_id'])
        .one_or_none())

    uid = new_staff['user_id']
    response = test_client.post(
        f'/user/email-verification/code/{uid}/?code={verification.code}')
    assert response.status_code == 200

    # Fetch staff user and ensure email is now verified
    user = User.query.filter_by(user_id=uid).one_or_none()
    assert user.email_verified == True

def test_get_staff_user_info(test_client, new_staff):
    uid = new_staff['user_id']
    response = test_client.get(
        f'/user/staff/{uid}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['staff_info']
    assert response.json['user_info']

def test_staff_login(test_client, new_staff):
    ###
    # Login (get token) for newly created staff member
    ##
    email = users_staff_new_user_data['user_info']['email']
    passw = users_staff_new_user_data['user_info']['password']
    creds = base64.b64encode(f'{email}:{passw}'.encode('utf-8')).decode('utf-8')

    headers = {'Authorization': f'Basic {creds}'}
    response = test_client.post(
        '/staff/token/',
        headers=headers,
        content_type='application/json')

    # ensure access roles are correctly returned
    roles = response.json['access_roles']

    # pull up login attempts by this client a new failed attempt should be in the database
    token_history = (test_client.db.session.execute(
        select(UserTokenHistory)
        .where(
            UserTokenHistory.user_id == response.json['user_id'])
        .order_by(
            UserTokenHistory.created_at.desc()))
        .all())

    assert response.status_code == 201
    assert roles.sort() == users_staff_new_user_data['staff_info']['access_roles'].sort()
    assert response.json['refresh_token'] == token_history[0][0].refresh_token
    assert token_history[0][0].event == 'login'

def test_creating_new_staff_same_email(test_client):
    response = test_client.post(
        '/user/staff/',
        headers=test_client.staff_auth_header,
        data=dumps(users_staff_new_user_data),
        content_type='application/json')

    # 409 should be returned because user email is already in use
    assert response.status_code == 409

def test_add_roles_to_staff(test_client, new_staff, new_staff_header):
    uid = new_staff['user_id']
    response = test_client.post(
        f'/staff/roles/{uid}/',
        headers=new_staff_header,
        data=dumps({'access_roles': STAFF_ROLES}),
        content_type='application/json')

    staff_roles = (
        test_client.db.session.execute(
            select(StaffRoles.role)
            .filter_by(
                user_id=uid))
        .scalars()
        .all())

    # some simple checks for validity
    assert response.status_code == 201
    assert sorted(staff_roles) == sorted(STAFF_ROLES)

def test_check_staff_roles(test_client, new_staff, new_staff_header):
    uid = new_staff['user_id']
    response = test_client.get(
        f'/staff/roles/{uid}/',
        headers=new_staff_header,
        content_type='application/json')

    staff_roles = (
        test_client.db.session.execute(
            select(StaffRoles.role)
            .filter_by(
                user_id=uid))
        .scalars()
        .all())

    # some simple checks for validity
    assert response.status_code == 200
    assert sorted(staff_roles) == sorted(STAFF_ROLES)

def test_add_staff_operational_territory(test_client, new_staff, new_staff_header):
    uid = new_staff['user_id']

    # pull up staff member and their current roles
    staff_roles = StaffRoles.query.filter_by(user_id=uid).all()

    possible_territories = (
        test_client.db.session.execute(
            select(LookupTerritoriesOfOperations.idx))
        .scalars()
        .all())

    # for each medical_doctor, trainer, nutritionist, physical_therapist
    # roles, randomly add a few territories of operation
    payload  = {'operational_territories' : []}
    for role in staff_roles:
        if role.role in ('medical_doctor', 'nutritionist', 'trainer', 'physical_therapist'):
            add_territories = random.sample(possible_territories, k=random.randint(1, len(possible_territories)))
            for territory in add_territories:
                payload['operational_territories'].append({
                    'role_id': role.idx,
                    'operational_territory_id': territory})

    response = test_client.post(
        f'/staff/operational-territories/{uid}/',
        headers=new_staff_header,
        data=dumps(payload),
        content_type='application/json')

    # bring up territories
    staff_territories = (
        StaffOperationalTerritories
        .query
        .filter_by(
            user_id=uid)
        .all())

    # some simple checks for validity
    assert response.status_code == 201
    assert len(staff_territories) == len(payload['operational_territories'])

def test_check_staff_operational_territories(test_client, new_staff, new_staff_header):
    uid = new_staff['user_id']

    response = test_client.get(
        f'/staff/operational-territories/{uid}/',
        headers=new_staff_header,
        content_type='application/json')

    # bring up territories
    staff_territories = (
        StaffOperationalTerritories
        .query
        .filter_by(
            user_id=uid)
        .all())

    # some simple checks for validity
    assert response.status_code == 200
    assert len(staff_territories) == len(response.json['operational_territories'])

def test_delete_staff_operational_territories(test_client, new_staff, new_staff_header):
    uid = new_staff['user_id']

    # pull up staff member and current operational territories
    staff_territories = (
        StaffOperationalTerritories
        .query
        .filter_by(
            user_id=uid)
        .all())

    delete_territories = random.sample(staff_territories, k=random.randint(1, len(staff_territories)))

    # build up payload of territories to delete from database
    payload  = {'operational_territories' : []}
    for territory in delete_territories:
        payload['operational_territories'].append({
            'role_id': territory.role_id,
            'operational_territory_id': territory.operational_territory_id})

    response = test_client.delete(
        f'/staff/operational-territories/{uid}/',
        headers=new_staff_header,
        data=dumps(payload),
        content_type='application/json')

    # bring up territories again
    staff_territories_refresh = (
        StaffOperationalTerritories
        .query
        .filter_by(
            user_id=uid)
        .all())

    # some simple checks for validity
    assert response.status_code == 204
    assert len(staff_territories_refresh) == len(staff_territories) - len(delete_territories)
