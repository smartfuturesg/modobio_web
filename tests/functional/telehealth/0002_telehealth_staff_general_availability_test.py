import time

from flask.json import dumps
from odyssey.api.staff.models import StaffRoles
from odyssey.api.payment.models import PaymentMethods

from odyssey.api.telehealth.models import (
    TelehealthStaffAvailability,
    TelehealthBookings,
    TelehealthQueueClientPool,
)
from odyssey.api.practitioner.models import PractitionerCredentials

from .data import (
    telehealth_staff_general_availability_1_post_data,
    telehealth_staff_general_availability_2_post_data,
    telehealth_staff_general_availability_3_post_data,
    telehealth_staff_general_availability_bad_3_post_data,
    telehealth_staff_general_availability_bad_4_post_data,
    telehealth_staff_general_availability_bad_5_post_data,
    telehealth_staff_general_availability_bad_6_post_data,
    telehealth_staff_general_availability_bad_7_post_data,
    telehealth_queue_client_pool_8_post_data
)
from tests.functional.doctor.data import doctor_credentials_post_1_data

def test_post_1_staff_general_availability(test_client, payment_method, staff_territory, staff_credentials, staff_consult_rate):
    # DEPENDENCY - add practitioner credentials
    response = test_client.post(
        f'/doctor/credentials/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(doctor_credentials_post_1_data),
        content_type='application/json')
    
    assert response.status_code == 201
    # DEPENDENCCY - add practitioner availability
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_1_post_data),
        content_type='application/json')
    
    assert response.status_code == 201

    telehealth_queue_client_pool_8_post_data['payment_method_id'] = payment_method.idx

    response = test_client.post(
        f'/telehealth/queue/client-pool/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(telehealth_queue_client_pool_8_post_data),
        content_type='application/json')

    # NOTE: At this point we have one staff member with availability 11 am - 12 pm on Mondays
    # this allows 3 avaiablities ==> 11 am, 11:15 am and 11:30 am
    # 11:45 and 12:00 are not valid start times bcs the practitioner's availablity ends at 12 pm
    # and the requested duration is 30 min.
    # NOTE: Availabilities are returned with this rule
    # At least 10 available time slots unless we have checked a full 2 weeks (14 days) off.
    # Thus, we will receive 9 availabilities, 3 on closest_future_Monday & 3 on closest_future_Monday + week & 3 on closest_future_Monday + 2 weeks
    response = test_client.get(
        f'/telehealth/client/time-select/{test_client.client_id}/',
        headers=test_client.client_auth_header)
    
    assert response.json['total_options'] == 9

    # 3_midnight_bug_staff_general_availability
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_3_post_data),
        content_type='application/json')
    
    assert response.status_code == 201

def test_get_3_staff_availability(test_client):
    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert [
        response.json['availability'][0]['day_of_week'],
        response.json['availability'][0]['start_time'],
        response.json['availability'][0]['end_time']] == ['Monday', '00:00:00', '12:00:00']

    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200

def test_post_2_staff_general_availability(test_client):
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_2_post_data),
        content_type='application/json')

    assert response.status_code == 201

def test_get_2_staff_availability(test_client):
    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert [
        response.json['availability'][0]['day_of_week'],
        response.json['availability'][0]['start_time'],
        response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00']
    assert [
        response.json['availability'][1]['day_of_week'],
        response.json['availability'][1]['start_time'],
        response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][2]['day_of_week'],
        response.json['availability'][2]['start_time'],
        response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00']
    assert [
        response.json['availability'][3]['day_of_week'],
        response.json['availability'][3]['start_time'],
        response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00']
    assert [
        response.json['availability'][4]['day_of_week'],
        response.json['availability'][4]['start_time'],
        response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][5]['day_of_week'],
        response.json['availability'][5]['start_time'],
        response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][6]['day_of_week'],
        response.json['availability'][6]['start_time'],
        response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']

def test_invalid_post_3_staff_general_availability(test_client):
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_bad_3_post_data),
        content_type='application/json')

    assert response.status_code == 400

def test_get_3_staff_availability(test_client):
    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert [
        response.json['availability'][0]['day_of_week'],
        response.json['availability'][0]['start_time'],
        response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00']
    assert [
        response.json['availability'][1]['day_of_week'],
        response.json['availability'][1]['start_time'],
        response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][2]['day_of_week'],
        response.json['availability'][2]['start_time'],
        response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00']
    assert [
        response.json['availability'][3]['day_of_week'],
        response.json['availability'][3]['start_time'],
        response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00']
    assert [
        response.json['availability'][4]['day_of_week'],
        response.json['availability'][4]['start_time'],
        response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][5]['day_of_week'],
        response.json['availability'][5]['start_time'],
        response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][6]['day_of_week'],
        response.json['availability'][6]['start_time'],
        response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']

def test_invalid_post_4_staff_general_availability(test_client):
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_bad_4_post_data),
        content_type='application/json')
    assert response.status_code == 400


def test_get_4_staff_availability(test_client):
    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert [
        response.json['availability'][0]['day_of_week'],
        response.json['availability'][0]['start_time'],
        response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00']
    assert [
        response.json['availability'][1]['day_of_week'],
        response.json['availability'][1]['start_time'],
        response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][2]['day_of_week'],
        response.json['availability'][2]['start_time'],
        response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00']
    assert [
        response.json['availability'][3]['day_of_week'],
        response.json['availability'][3]['start_time'],
        response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00']
    assert [
        response.json['availability'][4]['day_of_week'],
        response.json['availability'][4]['start_time'],
        response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][5]['day_of_week'],
        response.json['availability'][5]['start_time'],
        response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][6]['day_of_week'],
        response.json['availability'][6]['start_time'],
        response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']

def test_invalid_post_5_staff_general_availability(test_client):
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_bad_5_post_data),
        content_type='application/json')

    assert response.status_code == 400

def test_get_5_staff_availability(test_client):
    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert [
        response.json['availability'][0]['day_of_week'],
        response.json['availability'][0]['start_time'],
        response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00']
    assert [
        response.json['availability'][1]['day_of_week'],
        response.json['availability'][1]['start_time'],
        response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][2]['day_of_week'],
        response.json['availability'][2]['start_time'],
        response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00']
    assert [
        response.json['availability'][3]['day_of_week'],
        response.json['availability'][3]['start_time'],
        response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00']
    assert [
        response.json['availability'][4]['day_of_week'],
        response.json['availability'][4]['start_time'],
        response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][5]['day_of_week'],
        response.json['availability'][5]['start_time'],
        response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][6]['day_of_week'],
        response.json['availability'][6]['start_time'],
        response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']

def test_invalid_post_6_staff_general_availability(test_client):
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_bad_6_post_data),
        content_type='application/json')

    assert response.status_code == 400


def test_get_6_staff_availability(test_client):
    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert [
        response.json['availability'][0]['day_of_week'],
        response.json['availability'][0]['start_time'],
        response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00']
    assert [
        response.json['availability'][1]['day_of_week'],
        response.json['availability'][1]['start_time'],
        response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][2]['day_of_week'],
        response.json['availability'][2]['start_time'],
        response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00']
    assert [
        response.json['availability'][3]['day_of_week'],
        response.json['availability'][3]['start_time'],
        response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00']
    assert [
        response.json['availability'][4]['day_of_week'],
        response.json['availability'][4]['start_time'],
        response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][5]['day_of_week'],
        response.json['availability'][5]['start_time'],
        response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][6]['day_of_week'],
        response.json['availability'][6]['start_time'],
        response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']

def test_invalid_post_7_staff_general_availability(test_client):
    response = test_client.post(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(telehealth_staff_general_availability_bad_7_post_data),
        content_type='application/json')

    assert response.status_code == 400

def test_get_7_staff_availability(test_client):
    response = test_client.get(
        f'/telehealth/settings/staff/availability/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert [
        response.json['availability'][0]['day_of_week'],
        response.json['availability'][0]['start_time'],
        response.json['availability'][0]['end_time']] == ['Monday', '08:00:00', '09:00:00']
    assert [
        response.json['availability'][1]['day_of_week'],
        response.json['availability'][1]['start_time'],
        response.json['availability'][1]['end_time']] == ['Monday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][2]['day_of_week'],
        response.json['availability'][2]['start_time'],
        response.json['availability'][2]['end_time']] == ['Tuesday', '11:00:00', '13:00:00']
    assert [
        response.json['availability'][3]['day_of_week'],
        response.json['availability'][3]['start_time'],
        response.json['availability'][3]['end_time']] == ['Wednesday', '09:00:00', '20:00:00']
    assert [
        response.json['availability'][4]['day_of_week'],
        response.json['availability'][4]['start_time'],
        response.json['availability'][4]['end_time']] == ['Friday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][5]['day_of_week'],
        response.json['availability'][5]['start_time'],
        response.json['availability'][5]['end_time']] == ['Saturday', '13:00:00', '20:00:00']
    assert [
        response.json['availability'][6]['day_of_week'],
        response.json['availability'][6]['start_time'],
        response.json['availability'][6]['end_time']] == ['Sunday', '13:00:00', '20:00:00']
