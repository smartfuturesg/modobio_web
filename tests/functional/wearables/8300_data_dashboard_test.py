def test_data_dashboard_endpoint(
    test_client,
    oura_data,
):
    """
    Testing out the data dashboard endpoint. Ensuring that data is returned correctly
    and device switching works.
    """

    # test with OURA device using start_date and end_date as query params

    response = test_client.get(
        f"/v2/wearables/data/dashboard/{test_client.client_id}",
        headers=test_client.provider_auth_header,
        query_string={
            "start_date": oura_data["data_start_time"].strftime("%Y-%m-%d"),
            "end_date": oura_data["data_end_time"].strftime("%Y-%m-%d"),
            "default_wearable": "OURA",
        },
        content_type="application/json",
    )
    # ensure that all items from the WearablesV2DashboardOutputSchema schema are returned
    assert response.status_code == 200

    # top-level keys

    assert response.json["total_days"] == 2
    assert type(response.json.get("avg_resting_hr")) == float
    assert type(response.json.get("avg_steps")) == float
    assert type(response.json.get("avg_distance_feet")) == float
    assert type(response.json.get("avg_sleep_duration")) == float
    assert type(response.json.get("avg_in_bed_duration")) == float
    assert type(response.json.get("avg_calories")) == float
    assert type(response.json.get("avg_active_calories")) == float

    # keys nested under daily_metrics['2023-09-11']

    assert (
        type(response.json["daily_metrics"][0].get("total_duration_asleep"))
        == int
    )
    assert (
        type(response.json["daily_metrics"][0].get("total_duration_REM"))
        == int
    )
    assert (
        type(
            response.json["daily_metrics"][0].get(
                "total_duration_light_sleep"
            )
        )
        == int
    )
    assert (
        type(
            response.json["daily_metrics"][0].get(
                "total_duration_deep_sleep"
            )
        )
        == int
    )
    assert (
        type(response.json["daily_metrics"][0].get("total_duration_in_bed"))
        == int
    )
    assert type(response.json["daily_metrics"][0].get("resting_hr")) == int
    assert type(response.json["daily_metrics"][0].get("total_steps")) == int
    assert (
        type(response.json["daily_metrics"][0].get("total_distance_feet"))
        == float
    )
    assert (
        type(response.json["daily_metrics"][0].get("total_calories")) == int
    )
    assert (
        type(response.json["daily_metrics"][0].get("active_calories")) == int
    )
