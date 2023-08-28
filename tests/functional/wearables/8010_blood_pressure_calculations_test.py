import pytest
from datetime import datetime, timedelta

from .data import BLOOD_PRESSURE_WEARABLE, blood_pressure_data_1, blood_pressure_data_2


def test_blood_pressure_calculations_default_date_filters(
    test_client, add_blood_pressure_data
):
    # Test default date params. This should pick up both entries
    response = test_client.get(
        f"/v2/wearables/calculations/blood-pressure/30-day-hourly/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    # The Length of the response should always be 10. user_id, wearable, and 8 time_blocks
    assert len(response.json) == 10
    assert response.status_code == 200
    assert response.json.get("user_id") == test_client.client_id
    assert response.json.get("wearable") == BLOOD_PRESSURE_WEARABLE

    # All of our data will live in block_one and block_three because the hour of the timestamp in the mock data is always changed to these
    # For now, we can trust these calculations to be right. In the future, we can maybe manually calculate these values in the test to double check

    # Check block_three data
    assert response.json.get("block_three").get("average_systolic") == 85
    assert response.json.get("block_three").get("average_diastolic") == 125
    assert response.json.get("block_three").get("average_pulse") == 110
    assert response.json.get("block_three").get("max_systolic") == 90
    assert response.json.get("block_three").get("max_diastolic") == 130
    assert response.json.get("block_three").get("total_pulse_readings") == 2
    assert response.json.get("block_three").get("total_bp_readings") == 2
    assert response.json.get("block_three").get("min_diastolic") == 120
    assert response.json.get("block_three").get("min_systolic") == 80

    # Check block_one data
    assert response.json.get("block_one").get("average_systolic") == 78
    assert response.json.get("block_one").get("average_diastolic") == 138
    assert response.json.get("block_one").get("average_pulse") == 122
    assert response.json.get("block_one").get("max_systolic") == 85
    assert response.json.get("block_one").get("max_diastolic") == 140
    assert response.json.get("block_one").get("total_pulse_readings") == 2
    assert response.json.get("block_one").get("total_bp_readings") == 2
    assert response.json.get("block_one").get("min_diastolic") == 135
    assert response.json.get("block_one").get("min_systolic") == 70

    # Check that all other blocks are empty
    assert response.json.get("block_two").get("total_bp_readings") == 0
    assert response.json.get("block_two").get("total_pulse_readings") == 0
    assert response.json.get("block_four").get("total_bp_readings") == 0
    assert response.json.get("block_four").get("total_pulse_readings") == 0
    assert response.json.get("block_five").get("total_bp_readings") == 0
    assert response.json.get("block_five").get("total_pulse_readings") == 0
    assert response.json.get("block_six").get("total_bp_readings") == 0
    assert response.json.get("block_six").get("total_pulse_readings") == 0
    assert response.json.get("block_seven").get("total_bp_readings") == 0
    assert response.json.get("block_seven").get("total_pulse_readings") == 0
    assert response.json.get("block_eight").get("total_bp_readings") == 0
    assert response.json.get("block_eight").get("total_pulse_readings") == 0


def test_blood_pressure_calculations_start_date_param(
    test_client, add_blood_pressure_data
):
    # Test start date params. This should fail because we provide only 1 date param when we require both or neither
    response = test_client.get(
        f"/v2/wearables/calculations/blood-pressure/30-day-hourly/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=2)}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 400


def test_blood_pressure_calculations_end_date_param(
    test_client, add_blood_pressure_data
):
    # Test start date params. This should pick up only block_three data
    response = test_client.get(
        f"/v2/wearables/calculations/blood-pressure/30-day-hourly/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?end_date={datetime.utcnow() - timedelta(weeks=2)}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 400


def test_blood_pressure_calculations_start_and_end_date_params(
    test_client, add_blood_pressure_data
):
    # Test start date params. This should pick up no data
    response = test_client.get(
        f"/v2/wearables/calculations/blood-pressure/30-day-hourly/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=4)}&end_date={datetime.utcnow() - timedelta(weeks=4)}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    # The Length of the response should always be 10. user_id, wearable, and 8 time_blocks
    assert len(response.json) == 10
    assert response.status_code == 200
    assert response.json.get("user_id") == test_client.client_id
    assert response.json.get("wearable") == BLOOD_PRESSURE_WEARABLE

    # Check that all blocks are empty
    assert response.json.get("block_one").get("total_bp_readings") == 0
    assert response.json.get("block_one").get("total_pulse_readings") == 0
    assert response.json.get("block_two").get("total_bp_readings") == 0
    assert response.json.get("block_two").get("total_pulse_readings") == 0
    assert response.json.get("block_three").get("total_bp_readings") == 0
    assert response.json.get("block_three").get("total_pulse_readings") == 0
    assert response.json.get("block_four").get("total_bp_readings") == 0
    assert response.json.get("block_four").get("total_pulse_readings") == 0
    assert response.json.get("block_five").get("total_bp_readings") == 0
    assert response.json.get("block_five").get("total_pulse_readings") == 0
    assert response.json.get("block_six").get("total_bp_readings") == 0
    assert response.json.get("block_six").get("total_pulse_readings") == 0
    assert response.json.get("block_seven").get("total_bp_readings") == 0
    assert response.json.get("block_seven").get("total_pulse_readings") == 0
    assert response.json.get("block_eight").get("total_bp_readings") == 0
    assert response.json.get("block_eight").get("total_pulse_readings") == 0
