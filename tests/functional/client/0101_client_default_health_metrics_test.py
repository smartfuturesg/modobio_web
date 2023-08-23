import base64

from odyssey.api.user.models import UserPendingEmailVerifications
from flask.json import dumps


def test_get_default_health_metrics(test_client):
    ###
    # Fetch default metrics for a new client that does not have sex or age info in our system
    ###

    # make a new client with no sex of dob info
    new_client = {
        "firstname": "Testy",
        "email": "default_health_netric_client@modobio.com",
        "lastname": "Two",
        "phone_number": "2222223333",
        "password": "0987654321B",
    }

    response = test_client.post(
        "/user/client/", data=dumps(new_client), content_type="application/json"
    )

    assert response.status_code == 201

    new_user_id = response.json["user_info"]["user_id"]

    # Register the client's email address (token)
    verification = UserPendingEmailVerifications.query.filter_by(
        user_id=new_user_id
    ).one_or_none()
    token = verification.token

    response = test_client.get(f"/user/email-verification/token/{token}/")

    assert response.status_code == 200

    valid_credentials = base64.b64encode(
        f'{new_client["email"]}:0987654321B'.encode("utf-8")
    ).decode("utf-8")

    # get token
    headers = {"Authorization": f"Basic {valid_credentials}"}
    response = test_client.post(
        "/client/token/", headers=headers, content_type="application/json"
    )

    token = response.json.get("token")
    auth_header = {"Authorization": f"Bearer {token}"}

    # request default health metrics
    response = test_client.get(
        f"/client/default-health-metrics/{new_user_id}/",
        headers=auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["sex"] == "f"
    assert response.json["age"] == 30
