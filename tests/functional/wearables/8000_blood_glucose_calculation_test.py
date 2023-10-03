import pytest
from datetime import datetime, timedelta

from .data import blood_glucose_data_1, blood_glucose_data_2, BLOOD_GLUCOSE_WEARABLE


def test_blood_glucose_calculations_default_date_filters(
    test_client, add_blood_glucose_data
):
    # Test default date params. This should pick up only 1 entry
    response = test_client.get(
        f"/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )
    
    assert response.status_code == 200
    assert response.json.get("user_id") == test_client.client_id
    assert response.json.get("wearable") == BLOOD_GLUCOSE_WEARABLE
    assert response.json.get("average_glucose") == 125
    assert response.json.get("standard_deviation") == 35.4
    assert response.json.get("glucose_variability") == 28.3
    assert response.json.get("glucose_management_indicator") == 6.3


def test_blood_glucose_calculations_client_permission(
    test_client, add_blood_glucose_data
):
    # Test one client trying to access a different client wearable data. This should fail
    response = test_client.get(
        f"/v2/wearables/calculations/blood-glucose/{test_client.staff_id}/{BLOOD_GLUCOSE_WEARABLE}",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 401


def test_blood_glucose_calculations_start_date_param(
    test_client, add_blood_glucose_data
):
    # Test passing in a start_date of 4 weeks ago. This should fail because we didn't pass in both params or neither.
    response = test_client.get(
        f"/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=4)}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 400


def test_blood_glucose_calculations_end_date_param(test_client, add_blood_glucose_data):
    # Test passing in an end date of 3 days ago. This should fail because we didn't pass in both params or neither.
    response = test_client.get(
        f"/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?end_date={datetime.utcnow() - timedelta(days=3)}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 400


def test_blood_glucose_calculations_start_and_end_date_param(
    test_client, add_blood_glucose_data
):
    # Test passing in a start date of 4 weeks ago and end date of 2 weeks ago. This should pick up only 1 entry
    response = test_client.get(
        f"/v2/wearables/calculations/blood-glucose/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?start_date={datetime.utcnow() - timedelta(weeks=4)}&end_date={datetime.utcnow() - timedelta(weeks=2)}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json.get("user_id") == test_client.client_id
    assert response.json.get("wearable") == BLOOD_GLUCOSE_WEARABLE
    assert response.json.get("average_glucose") == 100
    assert response.json.get("standard_deviation") == 14.1
    assert response.json.get("glucose_variability") == 14.1
    assert response.json.get("glucose_management_indicator") == 5.7


def test_cgm_percentiles_calculation(test_client, add_cgm_data):
    start_time = add_cgm_data["data_start_time"]
    end_time = add_cgm_data["data_end_time"]

    response = test_client.get(
        f"/v2/wearables/calculations/blood-glucose/cgm/percentiles/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?start_date={start_time}&end_date={end_time}",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["bin_size_mins"] == 15
    assert response.json["data"][0]["minute"] == 0
    assert response.json["data"][0]["count"] == 42
    assert response.json["data"][0]["percentile_50th"] == 96.24
    assert response.json["data"][-1]["count"] == 42
    assert response.json["data"][-1]["percentile_75th"] == 114.09
    assert response.json["data"][-1]["minute"] == 1425
    assert len(response.json["data"]) == 96


def test_cgm_time_in_ranges_calculations(test_client, cgm_data_multi_range):
    start_time = cgm_data_multi_range[1]
    end_time = cgm_data_multi_range[2]

    response = test_client.get(
        f"/v2/wearables/calculations/blood-glucose/cgm/time-in-ranges/{test_client.client_id}/{BLOOD_GLUCOSE_WEARABLE}?start_date={start_time}&end_date={end_time}",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["user_id"] == test_client.client_id
    assert response.json["wearable"] == BLOOD_GLUCOSE_WEARABLE
    assert response.json["results"]["very_low_percentage"] == 6.0
    assert response.json["results"]["very_low_total_time"] == "1 h 23 min"
    assert response.json["results"]["low_percentage"] == 6.0
    assert response.json["results"]["low_total_time"] == "1 h 23 min"
    assert response.json["results"]["target_range_percentage"] == 60.0
    assert response.json["results"]["target_range_total_time"] == "13 h 48 min"
    assert response.json["results"]["high_percentage"] == 19.0
    assert response.json["results"]["high_total_time"] == "4 h 22 min"
    assert response.json["results"]["very_high_percentage"] == 9.0
    assert response.json["results"]["very_high_total_time"] == "2 h 4 min"
