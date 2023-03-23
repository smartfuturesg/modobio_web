import pytest
from datetime import datetime, timedelta

from .data import blood_glucose_data_1, blood_glucose_data_2, BLOOD_GLUCOSE_WEARABLE

def test_blood_glucose_calculations_default_date_filters(test_client, add_blood_glucose_data):

    # Test default date params. This should pick up only 1 entry
    response = test_client.get(
        f'/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_GLUCOSE_WEARABLE
    assert response.json.get('average_glucose') == 125
    assert response.json.get('standard_deviation') == 25
    assert response.json.get('glucose_variability') == 20
    assert response.json.get('glucose_management_indicator') == 6.3

def test_blood_glucose_calculations_client_permission(test_client, add_blood_glucose_data):

    # Test one client trying to access a different client wearable data. This should fail
    response = test_client.get(
        f'/v2/wearables/calculations/blood-glucose/{test_client.staff_id}/{BLOOD_GLUCOSE_WEARABLE}',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 401

def test_blood_glucose_calculations_start_date_param(test_client, add_blood_glucose_data):

    # Test passing in a start_date of 4 weeks ago. This should pick up both of our blood glucose entries
    response = test_client.get(
        f'/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=4)}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_GLUCOSE_WEARABLE
    assert response.json.get('average_glucose') == 112
    assert response.json.get('standard_deviation') == 22.8
    assert response.json.get('glucose_variability') == 20.2
    assert response.json.get('glucose_management_indicator') == 6.0

def test_blood_glucose_calculations_end_date_param(test_client, add_blood_glucose_data):

    # Test passing in an end date of 3 days ago. This shoudn't pick up any of our entries
    response = test_client.get(
        f'/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?end_date={datetime.utcnow() - timedelta(days=3)}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_GLUCOSE_WEARABLE
    assert response.json.get('average_glucose') == None
    assert response.json.get('standard_deviation') == None
    assert response.json.get('glucose_variability') == None
    assert response.json.get('glucose_management_indicator') == None

def test_blood_glucose_calculations_start_and_end_date_param(test_client, add_blood_glucose_data):

    # Test passing in a start date of 4 weeks ago and end date of 2 weeks ago. This should pick up only 1 entry 
    response = test_client.get(
        f'/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=4)}&end_date={datetime.utcnow() - timedelta(weeks=2)}',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_GLUCOSE_WEARABLE
    assert response.json.get('average_glucose') == 100
    assert response.json.get('standard_deviation') == 10
    assert response.json.get('glucose_variability') == 10
    assert response.json.get('glucose_management_indicator') == 5.7

def test_cgm_percentiles_calculation(test_client, add_cgm_data):
    start_time = add_cgm_data["data_start_time"]
    end_time = add_cgm_data["data_end_time"]

    response = test_client.get(
        f'/v2/wearables/calculations/blood-glucose/cgm/percentiles/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?start_date={start_time}&end_date={end_time}',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json["bin_size_mins"] == 15
    assert response.json["data"][0]["minute"] == 0
    assert response.json["data"][0]["count"] == 42
    assert response.json["data"][0]["percentile_50th"] == 96.24
    assert response.json["data"][-1]["count"] == 42
    assert response.json["data"][-1]["percentile_75th"] == 114.09
    assert response.json["data"][-1]["minute"] == 1425
    assert len(response.json["data"]) == 96
    
