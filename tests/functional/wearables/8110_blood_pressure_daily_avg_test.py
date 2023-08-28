from .data import BLOOD_PRESSURE_WEARABLE


def test_blood_pressure_daily_averages(test_client, bp_30_days_data):
    start_date = bp_30_days_data["data_start_time"]
    end_date = bp_30_days_data["data_end_time"]

    # provider in care team requesting BP daily averages
    response = test_client.get(
        f"/v2/wearables/calculations/blood-pressure/daily-average/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}?start_date={start_date}&end_date={end_date}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    assert response.json.get("total_items") == 24
    assert response.status_code == 200
