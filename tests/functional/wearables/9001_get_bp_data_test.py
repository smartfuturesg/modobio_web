from datetime import datetime, timedelta
import json

from tests.functional.wearables.data import BLOOD_PRESSURE_WEARABLE


def test_get_bp_data(test_client, add_blood_pressure_data):
    """Returns blood pressure data from all sources"""

    response = test_client.get(
        f"/v2/wearables/data/blood-pressure/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    data = response.json

    assert response.status_code == 200
    assert data.get("total_items") == 2


def test_get_bp_data_with_dates(test_client, add_blood_pressure_data):
    start_date = datetime.utcnow() - timedelta(weeks=6)
    end_date = datetime.utcnow() - timedelta(weeks=5)
    response = test_client.get(
        f"/v2/wearables/data/blood-pressure/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )
    data = response.json

    assert response.status_code == 200
    assert data.get("total_items") == 0
