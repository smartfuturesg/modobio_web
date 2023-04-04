import pytest
from datetime import datetime, timedelta

from .data import BLOOD_PRESSURE_WEARABLE, blood_pressure_data_1, blood_pressure_data_2

def test_blood_pressure_monitoring_statistics_default(test_client, add_blood_pressure_data):

    # Test default start_date - this should pick up all 4 of our test samples
    response = test_client.get(
        f'/v2/wearables/calculations/blood-pressure/monitoring-statistics/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    # The Length of the response should always be 4: user_id, wearable, current_block, and prev_block
    assert len(response.json) == 4
    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_PRESSURE_WEARABLE

    # Current block general data
    assert response.json.get('current_block').get('general_data').get('average_systolic') == 81
    assert response.json.get('current_block').get('general_data').get('average_diastolic') == 131
    assert response.json.get('current_block').get('general_data').get('total_bp_readings') == 4
    assert response.json.get('current_block').get('general_data').get('total_pulse_readings') == 4
    assert response.json.get('current_block').get('general_data').get('average_pulse') == 116
    assert response.json.get('current_block').get('general_data').get('average_readings_per_day') == 0.13

    # Current block classification data
    assert response.json.get('current_block').get('classification_data').get('normal') == 0
    assert response.json.get('current_block').get('classification_data').get('elevated') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_1') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_2') == 1
    assert response.json.get('current_block').get('classification_data').get('hypertensive_crisis') == 3
    assert response.json.get('current_block').get('classification_data').get('normal_percentage') == 0
    assert response.json.get('current_block').get('classification_data').get('elevated_percentage') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_1_percentage') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_2_percentage') == 25
    assert response.json.get('current_block').get('classification_data').get('hypertensive_crisis_percentage') == 75

    # Previous block data - make sure there's nothing here
    assert response.json.get('prev_block').get('general_data').get('total_bp_readings') == None
    assert response.json.get('prev_block').get('general_data').get('total_pulse_readings') == None

def test_blood_pressure_monitoring_statistics_start_date_param(test_client, add_blood_pressure_data):

    # Test default start_date - this should pick up all 4 of our test samples, but split them up 2 in current_block and 2 in prev_block
    response = test_client.get(
        f'/v2/wearables/calculations/blood-pressure/monitoring-statistics/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=2)}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    # The Length of the response should always be 4: user_id, wearable, current_block, and prev_block
    assert len(response.json) == 4
    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_PRESSURE_WEARABLE

    # Current block general data
    assert response.json.get('current_block').get('general_data').get('average_systolic') == 77
    assert response.json.get('current_block').get('general_data').get('average_diastolic') == 137
    assert response.json.get('current_block').get('general_data').get('total_bp_readings') == 2
    assert response.json.get('current_block').get('general_data').get('total_pulse_readings') == 2
    assert response.json.get('current_block').get('general_data').get('average_pulse') == 122
    assert response.json.get('current_block').get('general_data').get('average_readings_per_day') == 0.14

    # Current block classification data
    assert response.json.get('current_block').get('classification_data').get('normal') == 0
    assert response.json.get('current_block').get('classification_data').get('elevated') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_1') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_2') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertensive_crisis') == 2
    assert response.json.get('current_block').get('classification_data').get('normal_percentage') == 0
    assert response.json.get('current_block').get('classification_data').get('elevated_percentage') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_1_percentage') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertension_stage_2_percentage') == 0
    assert response.json.get('current_block').get('classification_data').get('hypertensive_crisis_percentage') == 100

    # Previous block general data
    assert response.json.get('prev_block').get('general_data').get('average_systolic') == 85
    assert response.json.get('prev_block').get('general_data').get('average_diastolic') == 125
    assert response.json.get('prev_block').get('general_data').get('total_bp_readings') == 2
    assert response.json.get('prev_block').get('general_data').get('total_pulse_readings') == 2
    assert response.json.get('prev_block').get('general_data').get('average_pulse') == 110
    assert response.json.get('prev_block').get('general_data').get('average_readings_per_day') == 0.14

    # Previous block classification data
    assert response.json.get('prev_block').get('classification_data').get('normal') == 0
    assert response.json.get('prev_block').get('classification_data').get('elevated') == 0
    assert response.json.get('prev_block').get('classification_data').get('hypertension_stage_1') == 0
    assert response.json.get('prev_block').get('classification_data').get('hypertension_stage_2') == 1
    assert response.json.get('prev_block').get('classification_data').get('hypertensive_crisis') == 1
    assert response.json.get('prev_block').get('classification_data').get('normal_percentage') == 0
    assert response.json.get('prev_block').get('classification_data').get('elevated_percentage') == 0
    assert response.json.get('prev_block').get('classification_data').get('hypertension_stage_1_percentage') == 0
    assert response.json.get('prev_block').get('classification_data').get('hypertension_stage_2_percentage') == 50
    assert response.json.get('prev_block').get('classification_data').get('hypertensive_crisis_percentage') == 50

def test_blood_pressure_monitoring_statistics_unauthorized(test_client, add_blood_pressure_data):

    # Test client 16 using client 17 auth header. This should fail
    other_client_id = 16

    response = test_client.get(
        f'/v2/wearables/calculations/blood-pressure/monitoring-statistics/{other_client_id}/{BLOOD_PRESSURE_WEARABLE}',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 401
    

    
