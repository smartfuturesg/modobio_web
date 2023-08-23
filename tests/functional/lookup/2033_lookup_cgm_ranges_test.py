def test_get_cgm_ranges(test_client):
    response = test_client.get(
        "/lookup/blood-glucose/cgm/ranges/",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200


def test_get_cgm_demographics(test_client):
    response = test_client.get(
        "/lookup/blood-glucose/cgm/demographics/",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
