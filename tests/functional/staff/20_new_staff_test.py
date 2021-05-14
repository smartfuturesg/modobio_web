import base64
import random

from flask.json import dumps
from sqlalchemy import select

from odyssey.api.lookup.models import LookupTerritoriesofOperation
from odyssey.api.user.models import User, UserPendingEmailVerifications, UserTokenHistory
from odyssey.api.staff.models import StaffOperationalTerritories, StaffRoles
from odyssey.utils.constants import ACCESS_ROLES
from odyssey import db
from .data import users_staff_new_user_data


def test_creating_new_staff(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff' resource  is requested to be created
    THEN check the response is valid
    """
    # get staff authorization to view client data
    global new_staff_uid
    
    
    response = test_client.post('/user/staff/',
                                headers=staff_auth_header, 
                                data=dumps(users_staff_new_user_data), 
                                content_type='application/json')
    
    new_staff_uid = response.json['user_info']['user_id']
    # some simple checks for validity
    assert response.status_code == 201
    assert response.json['user_info']['firstname'] == users_staff_new_user_data['user_info']['firstname']
    assert response.json['user_info']['is_staff'] == True
    assert response.json['user_info']['is_client'] == False
    assert response.json['user_info']['email_verified'] == False

    # Register the staff's email address (code)
    verification = UserPendingEmailVerifications.query.filter_by(user_id=new_staff_uid).one_or_none()
    code = verification.code

    response = test_client.post(f'/user/email-verification/code/{new_staff_uid}/?code={code}')
    assert response.status_code == 200

    # Fetch staff user and ensure email is now verified
    user = User.query.filter_by(user_id=new_staff_uid).one_or_none()
    assert user.email_verified == True

def test_get_staff_user_info(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for retrieving staff and user info
    WHEN the '/staff/user_id' resource  is requested
    THEN check the response is valid
    """
    response = test_client.get(f'/user/staff/{new_staff_uid}/',
                                headers=staff_auth_header, 
                                content_type='application/json')

    assert response.status_code == 200
    assert response.json['staff_info']
    assert response.json['user_info']

                
def test_staff_login(test_client, init_database, staff_auth_header):
    """
    GIVEN a api fr requesting an API access token
    WHEN the 'tokens/staff/' resource  is requested to be created
    THEN check the response is valid
    """
    
    ###
    # Login (get token) for newly created staff member
    ##
    valid_credentials = base64.b64encode(
        f"{users_staff_new_user_data['user_info']['email']}:{users_staff_new_user_data['user_info']['password']}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')
    
    # ensure access roles are correctly returned
    roles = response.get_json()['access_roles']

    # pull up login attempts by this client a new failed attempt should be in the database
    token_history = init_database.session.execute(
            select(UserTokenHistory). \
            where(UserTokenHistory.user_id==response.json['user_id']). \
            order_by(UserTokenHistory.created_at.desc())
        ).all()

    assert response.status_code == 201
    assert roles.sort() == users_staff_new_user_data['staff_info']['access_roles'].sort()
    assert response.json['refresh_token'] == token_history[0][0].refresh_token
    assert token_history[0][0].event == 'login'

def test_creating_new_staff_same_email(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for creating a new staff 
    WHEN the '/staff/' resource  is requested to be created
    THEN check the response is 409 error
    """   
    response = test_client.post('/user/staff/',
                                headers=staff_auth_header, 
                                data=dumps(users_staff_new_user_data), 
                                content_type='application/json')
                                
    # 409 should be returned because user email is already in use
    assert response.status_code == 409


def test_add_roles_to_staff(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for updating a staff member's roles 
    WHEN the '/staff/roles/<user_id>/' resource  is requested to be created
    THEN check the response is valid
    """
    # get staff authorization to view client data
    staff = User.query.filter_by(email='staff_member@modobio.com').first()
    payload = {'access_roles': ACCESS_ROLES}
    response = test_client.post(f'/staff/roles/{staff.user_id}/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')
    
    staff_roles = StaffRoles.query.filter_by(user_id=staff.user_id).all()
    staff_roles = [x.role for x in staff_roles]
    
    # some simple checks for validity
    assert response.status_code == 201
    assert sorted(staff_roles) == sorted(ACCESS_ROLES)

def test_check_staff_roles(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for checking a staff member's roles 
    WHEN the '/staff/roles/<user_id>/' resource  is requested GET
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(email='staff_member@modobio.com').first()
    response = test_client.get(f'/staff/roles/{staff.user_id}/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    
    staff_roles = StaffRoles.query.filter_by(user_id=staff.user_id).all()
    staff_roles = [x.role for x in staff_roles]
    
    # some simple checks for validity
    assert response.status_code == 200
    assert sorted(staff_roles) == sorted(ACCESS_ROLES)

def test_add_staff_operational_territory(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for adding operational territories to a staff member's account
    WHEN the '/staff/operational-territories/<user_id>/' resource  is requested to be created
    THEN check the response is valid
    """
    # pull up staff member and their current roles
    staff = User.query.filter_by(email='staff_member@modobio.com').first()
    staff_roles = StaffRoles.query.filter_by(user_id = staff.user_id).all()

    possible_territories = init_database.session.query(LookupTerritoriesofOperation.idx).all()
    possible_territories = [x[0] for x in possible_territories]
    payload  = {'operational_territories' : []}

    # for each doctor, trainer, nutritionist, physical_therapist role randomly add a few territories of operation
    for role in staff_roles:
        if role.role in ('doctor', 'nutrition', 'trainer', 'physical_therapist'):
            add_territories = random.sample(possible_territories, k=random.randint(1, len(possible_territories)))
            for territory in add_territories:
                payload['operational_territories'].append({'role_id': role.idx, 
                                                           'operational_territory_id': territory})

    
    response = test_client.post(f'/staff/operational-territories/{staff.user_id}/',
                                headers=staff_auth_header, 
                                data=dumps(payload), 
                                content_type='application/json')

    # bring up territories
    staff_territories = StaffOperationalTerritories.query.filter_by(user_id = staff.user_id).all()
    
    # some simple checks for validity
    assert response.status_code == 201
    assert len(staff_territories) == len(payload['operational_territories'])

def test_check_staff_operational_territories(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for checking a staff member's operational territories 
    WHEN the '/staff/operational-territories/<user_id>/' resource  is requested GET
    THEN check the response is valid
    """

    # get staff authorization to view client data
    staff = User.query.filter_by(is_staff=True).first()
    response = test_client.get(f'/staff/operational-territories/{staff.user_id}/',
                                headers=staff_auth_header, 
                                content_type='application/json')
    # bring up territories
    staff_territories = StaffOperationalTerritories.query.filter_by(user_id = staff.user_id).all()
    
    # some simple checks for validity
    assert response.status_code == 200
    assert len(staff_territories) == len(response.json['operational_territories'])

def test_delete_staff_operational_territories(test_client, init_database, staff_auth_header):
    """
    GIVEN a api end point for deleting a staff member's operational territories 
    WHEN the '/staff/operational-territories/<user_id>/' resource  is requested GET
    THEN check the response is valid
    """

    # pull up staff member and current operational territories
    staff = User.query.filter_by(email='staff_member@modobio.com').first()
    staff_territories = StaffOperationalTerritories.query.filter_by(user_id = staff.user_id).all()


    delete_territories = random.sample(staff_territories, k=random.randint(1, len(staff_territories)))

    # build up payload of territories to delete from database
    payload  = {'operational_territories' : []}
    for territory in delete_territories:
        payload['operational_territories'].append({'role_id': territory.role_id, 
                                                   'operational_territory_id': territory.operational_territory_id})

    response = test_client.delete(f'/staff/operational-territories/{staff.user_id}/',
                                headers=staff_auth_header, 
                                data=dumps(payload),
                                content_type='application/json')

    # bring up territories again
    staff_territories_refresh = StaffOperationalTerritories.query.filter_by(user_id = staff.user_id).all()
    # some simple checks for validity
    assert response.status_code == 204
    assert len(staff_territories_refresh) == len(staff_territories)-len(delete_territories)