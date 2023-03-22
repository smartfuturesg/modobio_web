from datetime import datetime, timedelta
import uuid
import pytest

from odyssey.api.wearables.models import WearablesV2
from .data import BLOOD_PRESSURE_WEARABLE, test_8100_data_past_week, test_8100_data_week_to_month_ago


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
    # assert response.json.get('diastolic_bp_coefficient_of_variation') is None
    # assert response.json.get('systolic_bp_coefficient_of_variation') is None

    # breakpoint()


@pytest.mark.skip('DEV')
def test_blood_pressure_calculations_extended_date_filters(test_client, bp_data_fixture):
    response = test_client.get(
        f'/v2/wearables/calculations/blood-pressure/variation/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?start_date{datetime.utcnow() - timedelta(weeks=40)}=&end_date={datetime.utcnow() + timedelta(weeks=1)}',
        headers=test_client.staff_auth_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json.get('user_id') == test_client.client_id
    assert response.json.get('wearable') == BLOOD_PRESSURE_WEARABLE
    assert response.json.get('diastolic_bp_avg') == 72
    assert response.json.get('systolic_bp_avg') == 131
    # assert response.json.get('diastolic_standard_deviation') == 4
    # assert response.json.get('systolic_standard_deviation') == 10
    # assert response.json.get('diastolic_bp_coefficient_of_variation') is None
    # assert response.json.get('systolic_bp_coefficient_of_variation') is None

    # breakpoint()
