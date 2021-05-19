import base64
from datetime import datetime
import os
import pytest
import copy

from flask_migrate import upgrade
from sqlalchemy import text
from sqlalchemy.sql.expression import select
from twilio.rest import Client, TwilioException

from odyssey import create_app, db
from odyssey.api.client.models import ClientInfo
from odyssey.api.facility.models import MedicalInstitutions
from odyssey.api.staff.models import StaffProfile, StaffRoles
from odyssey.api.user.models import User, UserLogin
from odyssey.api.user.schemas import UserSubscriptionsSchema
from odyssey.utils.constants import ACCESS_ROLES
from odyssey.utils.misc import grab_twilio_credentials
from tests.functional.user.data import users_staff_member_data, users_client_new_creation_data, users_client_new_info_data
from odyssey.utils import search

@pytest.fixture(scope='session')
def delete_users():
    ''' Delete users that were generated for telehealth
    '''
    all_users = User.query.all()
    skipEmails = ['new_client_1','new_staff_1']
    modo_ids = []
    for user in all_users:
        tmpEmail = user.email
        tmpEmailArr = tmpEmail.split('@')
        if tmpEmailArr[0] in skipEmails:
            continue
        if tmpEmailArr[0][-1].isnumeric():
            modo_ids.append(user.modobio_id)
            # db.session.delete(user)
    # remove modo_ids from twilio        
    clear_twilio(modobio_ids=modo_ids)
    # db.session.commit()

@pytest.fixture(scope='session')
def generate_users():
    ''' This function is used to generate an equal number of clients and
        staff
        numUsers = 10 
        this will create 10 clients and 10 staff
    '''
    numUsers=10
    # 1) Create User instance. modobio_id populated automatically
    origClientEmail = copy.deepcopy(users_client_new_creation_data['email'])
    origStaffEmail = copy.deepcopy(users_staff_member_data['email'])
    base_modo_id_client = 'KW99TSVWP88'
    base_modo_id_staff = 'ZW99TSVWP88'
    for i in range(numUsers):
        # Change the email
        tmpEmail = users_client_new_creation_data['email'].split('@')
        tmpEmail[0]+=str(i)
        client_modobio_id = base_modo_id_client+str(i)
        users_client_new_creation_data['email'] = tmpEmail[0] + '@' + tmpEmail[1]
        users_client_new_creation_data['phone_number'] = str(90 + i)
        client_1 = User(**users_client_new_creation_data)
        client_1.email_verified = True
        db.session.add(client_1)
        db.session.flush()

        client_1.modobio_id = client_modobio_id
        db.session.add(client_1)
        # 2) User login
        client_1_login = UserLogin(**{'user_id': client_1.user_id})
        client_1_login.set_password('password')
        
        # 3) Client info
        users_client_new_info_data['user_id'] = client_1.user_id
        client_1_info = ClientInfo(**users_client_new_info_data)
        client_1_sub = UserSubscriptionsSchema().load({
        'subscription_type_id': 1,
        'subscription_status': 'unsubscribed',
        'is_staff': False
        })
        client_1_sub.user_id = client_1.user_id
        db.session.add(client_1_login)
        db.session.add(client_1_info)
        db.session.add(client_1_sub)
        db.session.flush()


        ####
        # initialize a test staff member
        ####
        tmpEmailStaff = users_staff_member_data['email'].split('@')
        tmpEmailStaff[0]+=str(i)
        staff_modobio_id = base_modo_id_staff+str(i)
        users_staff_member_data['email'] = tmpEmailStaff[0] + '@' + tmpEmailStaff[1]
        users_staff_member_data['phone_number'] = str(30 + i)
        # 1) Create User where is_staff is True
        staff_1 = User(**users_staff_member_data)
        staff_1.email_verified = True
        db.session.add(staff_1)
        db.session.flush()

        staff_1.modobio_id = staff_modobio_id
        db.session.add(staff_1)
        # 2) Enter login details for this staff memebr
        staff_1_login = UserLogin(**{"user_id": staff_1.user_id})
        staff_1_login.set_password('password')
        db.session.add(staff_1_login)

        # 3) give staff member all roles
        
        if i < 5:
            db.session.add(StaffRoles(user_id=staff_1.user_id, role='medical_doctor', verified=True))
        else:
            for idx,role in enumerate(ACCESS_ROLES):
                db.session.add(StaffRoles(user_id=staff_1.user_id, role=role, verified=True))

        # 4) Staff Profile
        staff_profile = StaffProfile(**{"user_id": staff_1.user_id})
        db.session.add(staff_profile)
        db.session.flush()
        users_client_new_creation_data['email'] = origClientEmail
        users_staff_member_data['email'] = origStaffEmail
    db.session.commit()


def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        try:
            db.session.execute(text(table.delete()))
        except:
            pass
    db.session.commit()
    # specifically cascade drop clientinfo table
    try:
        db.session.execute(text("DROP TABLE \"ClientInfo\" CASCADE;"))
    except:
        db.session.rollback()
        pass

    try:
        db.session.execute(text("DROP TABLE alembic_version;"))
    except Exception as e:
        pass

    db.session.commit()
    db.drop_all()

def clear_twilio(db=None, modobio_ids=None):
    # XXX: temporary fix for failing Twilio tests
    # return
    # bring up users
    if not modobio_ids:
        modobio_ids = db.session.execute(
            select(User.modobio_id)
        ).scalars().all()
    
    twilio_credentials = grab_twilio_credentials()
    client = Client(twilio_credentials['api_key'], 
                    twilio_credentials['api_key_secret'],
                    twilio_credentials['account_sid'])
    for modo_id in modobio_ids:
        try:
            client.conversations.users(modo_id).delete()
        except TwilioException as e:
            # error will arise from user not being in twilio
            continue

@pytest.fixture(scope='session')
def init_database():
    clean_db(db)

    # create db from migrations
    try:
        upgrade()
    except:
        pytest.exit(msg="migration failed")

    # run .sql files to create db procedures and initialize 
    # some tables
    #  read .sql files, remove comments,
    #  execute, raw sql on database
    sql_scripts = ['database/'+f for f in os.listdir('database/') if f.endswith(".sql")]
    for sql_script in sql_scripts:
        if 'seed_users' in sql_script:
            continue
        with open (sql_script, "r") as f:
            data=f.readlines()

        dat = [x for x in data if not x.startswith('--')]
    
        db.session.execute(text(''.join(dat)))

    # seed test users
    with open ("tests/seed_test_users.sql", "r") as f:
            data=f.readlines()

    dat = [x for x in data if not x.startswith('--')]
    
    db.session.execute(text(''.join(dat)))

    # 4) Add Client info and subscription date
    users_client_new_info_data['user_id'] = 1
    client_1_info = ClientInfo(**users_client_new_info_data)
    client_1_sub = UserSubscriptionsSchema().load({
    'subscription_type_id': 1,
    'subscription_status': 'unsubscribed',
    'is_staff': False
    })
    client_1_sub.user_id = 1
    db.session.add(client_1_info)
    db.session.add(client_1_sub)
    db.session.flush()

    ####
    # initialize a test staff member
    ####

    #  give staff member all roles
    for role in ACCESS_ROLES:
        db.session.add(StaffRoles(user_id=2, role=role, verified=True))
        
    # Add Staff Profile
    staff_profile = StaffProfile(**{"user_id": 2})
    db.session.add(staff_profile)
    db.session.flush()

    #initialize Medical institutes table
    med_institute1 = MedicalInstitutions(institute_name='Mercy Gilbert Medical Center')
    med_institute2 = MedicalInstitutions(institute_name='Mercy Tempe Medical Center')

    db.session.add_all([med_institute1, med_institute2])
    # db.session.add_all([med_institute1, med_institute2])

    # Commit the changes for the users
    db.session.commit()
    #add elastic search build index
    search.build_ES_indices()
    
    yield db  # this is where the testing happens!
    
    # https://stackoverflow.com/questions/26350911/what-to-do-when-a-py-test-hangs-silently
    db.session.close()
    
    clear_twilio(db)
    
    clean_db(db)


@pytest.fixture(scope='session')
def test_client():
    """flask application instance (client)"""
    app = create_app()
    db.init_app(app)
    testing_client = app.test_client()
    
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    
    yield testing_client

    ctx.pop()

@pytest.fixture(scope='session')
def staff_auth_header(test_client):
    ###
    # Login (get token) for newly created staff member
    ##


    valid_credentials = base64.b64encode(
        f"{users_staff_member_data['email']}:{'password'}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/staff/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')

    auth_header = {'Authorization': f'Bearer {token}'}
    
    yield auth_header

@pytest.fixture(scope='session')
def client_auth_header(test_client):
    ###
    # Login (get token) for newly created client member
    ##

    valid_credentials = base64.b64encode(
        f"{users_client_new_creation_data['email']}:{'password'}".encode(
            "utf-8")).decode("utf-8")
    
    headers = {'Authorization': f'Basic {valid_credentials}'}
    response = test_client.post('/client/token/',
                            headers=headers, 
                            content_type='application/json')
    token = response.json.get('token')

    auth_header = {'Authorization': f'Bearer {token}'}
    
    yield auth_header
