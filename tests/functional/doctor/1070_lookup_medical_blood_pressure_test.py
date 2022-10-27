# Test blood pressure look up
def test_get_blood_pressure_ranges(test_client):
    response = test_client.get(
        '/doctor/lookupbloodpressureranges/',
        headers=test_client.provider_auth_header)

    assert response.status_code == 200
    assert response.json['total_items'] == 5
    assert len(response.json['items']) == 5
