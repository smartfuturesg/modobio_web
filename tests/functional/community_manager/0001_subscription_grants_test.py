from flask.json import dumps

from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants


def test_post_subscription_grant(test_client):
    data = {
        "emails": ["client@modobio.com", "not_a_user@gmail.com"],
        "modobio_ids": ["TC12JASDFF12"],
        "sponsor": "Sponsoring Institution",
        "subscription_type_id": 2,
    }

    response = test_client.post(
        f"/community-manager/subscriptions/grant",
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type="application/json",
    )

    # bring up grants
    grants = CommunityManagerSubscriptionGrants.query.filter_by(
        user_id=test_client.staff_id
    ).all()

    assert response.status_code == 200
    assert len(grants) == 2


def test_post_subscription_grant_bad_modo_id(test_client):
    data = {
        "emails": ["client@modobio.com", "not_a_user@gmail.com"],
        "modobio_ids": ["TCXXXXXXXXXX"],
        "sponsor": "Sponsoring Institution",
        "subscription_type_id": 2,
    }

    response = test_client.post(
        f"/community-manager/subscriptions/grant",
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type="application/json",
    )

    assert response.status_code == 400


def test_get_subscriptions_granted(test_client, subscription_grants):
    response = test_client.get(
        f"/community-manager/subscriptions/grant",
        headers=test_client.staff_auth_header,
        content_type="application/json",
    )

    # bring up grants

    assert response.status_code == 200
