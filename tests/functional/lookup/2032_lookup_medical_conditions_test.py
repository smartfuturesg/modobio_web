def test_get_medical_conditions(test_client):
    response = test_client.get(
        "/lookup/medicalconditions/", headers=test_client.staff_auth_header
    )

    assert response.status_code == 200
    assert response.json["total_items"] == 276
    assert len(response.json["items"]) == 276
