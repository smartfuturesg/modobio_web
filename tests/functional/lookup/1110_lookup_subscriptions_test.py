from flask.json import dumps


def test_get_subscription_types(test_client):
    response = test_client.get(
        "/lookup/subscriptions/",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["items"][1]["name"] == "Monthly"
    assert response.json["items"][0]["cost"] == 97.99
    assert response.json["items"][1]["google_product_id"]
    assert response.json["items"][1]["ios_product_id"]
