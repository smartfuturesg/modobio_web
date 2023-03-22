from datetime import datetime, timedelta

from .data import BLOOD_PRESSURE_WEARABLE


def test_blood_pressure_calculations_default_date_filters(test_client, bp_data_fixture):
    response = test_client.get(
        f'/v2/wearables/calculations/blood-pressure/variation/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}',
        headers=test_client.staff_auth_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_PRESSURE_WEARABLE
    assert response.json.get('diastolic_bp_avg') == 72
    assert response.json.get('systolic_bp_avg') == 131
    assert response.json.get('diastolic_standard_deviation') == 5
    assert response.json.get('systolic_standard_deviation') == 10
    assert response.json.get('diastolic_bp_coefficient_of_variation') == 6
    assert response.json.get('systolic_bp_coefficient_of_variation') == 8


def test_blood_pressure_calculations_extended_date_filters(test_client, bp_data_fixture):
    response = test_client.get(
        f'/v2/wearables/calculations/blood-pressure/variation/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=40)}&end_date={datetime.utcnow() + timedelta(weeks=1)}',
        headers=test_client.staff_auth_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_PRESSURE_WEARABLE
    assert response.json.get('diastolic_bp_avg') == 76
    assert response.json.get('systolic_bp_avg') == 129
    assert response.json.get('diastolic_standard_deviation') == 11
    assert response.json.get('systolic_standard_deviation') == 13
    assert response.json.get('diastolic_bp_coefficient_of_variation') == 14
    assert response.json.get('systolic_bp_coefficient_of_variation') == 10
