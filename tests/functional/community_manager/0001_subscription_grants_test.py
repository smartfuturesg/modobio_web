from flask.json import dumps

from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.user.models import User, UserPendingEmailVerifications, UserSubscriptions
from odyssey.utils.misc import EmailVerification
from tests.utils import login



def test_post_subscription_grant(test_client):
    """
    POST subscription grants for user by email and modobio_id. Also POST subscription grant for non-user
    
    """
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

    # teardown, delete subscription and grants
    UserSubscriptions.query.filter_by(user_id = test_client.client_id, subscription_status = 'subscribed').delete()
    CommunityManagerSubscriptionGrants.query.filter_by(
        user_id=test_client.staff_id
    ).delete()
    test_client.db.session.commit()

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

def test_post_subscription_grant_unverified_user(test_client, unverified_user):
    """
    Test adding subscription grant for an unverified user. 

    Subscription grant should be stored and the user's subscription state should not be updated
    until the user verifies their email
    
    """
    user, email_verification = unverified_user
    # post grant for user
    data = {
        "emails": [user.email],
        "modobio_ids": [],
        "sponsor": "Sponsoring Institution",
        "subscription_type_id": 2,
    }

    response = test_client.post(
        f"/community-manager/subscriptions/grant",
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type="application/json",
    )

    # bring up subscriptions to verify nothing has been updated
    subscriptions = UserSubscriptions.query.filter_by(user_id = user.user_id).all()
    grants = CommunityManagerSubscriptionGrants.query.filter_by(
        subscription_grantee_user_id=user.user_id
    ).all()

    assert response.status_code == 200
    assert len(subscriptions) == 1
    assert len(grants) == 1

    # verify user and check that subscription has been updated
    EmailVerification().complete_email_verification(user_id = user.user_id, code = email_verification["code"])

    subscriptions = UserSubscriptions.query.filter_by(user_id = user.user_id).all()
    assert len(subscriptions) == 2
    assert subscriptions[1].subscription_status == 'subscribed'

def test_post_subscription_grant_non_user(test_client):
    """ Test adding subscription grant for a non-user. """
    non_user_email = "not_a_user_yet@test.com"
    # post grant for user
    data = {
        "emails": [non_user_email],
        "modobio_ids": [],
        "sponsor": "Sponsoring Institution",
        "subscription_type_id": 2,
    }

    response = test_client.post(
        f"/community-manager/subscriptions/grant",
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type="application/json",
    )

    # send a post request to create a user
    data = {
            "firstname": "Not",
            "email": non_user_email,
            "lastname": "A User",
            "password": "123",
            "phone_number": "1234567890",
        }
    response = test_client.post("/user/client/", data=dumps(data), content_type="application/json")

    user_id = response.json["user_info"]["user_id"]

    # bring up subscriptions to verify no thing has been updated yet
    subscriptions = UserSubscriptions.query.filter_by(user_id = user_id).all()

    assert len(subscriptions) == 1
    
    # verify user email
    email_verification = UserPendingEmailVerifications.query.filter_by(user_id = user_id).first()
    EmailVerification().complete_email_verification(user_id = user_id, code = email_verification.code)

    # assure subscription grant has been applied
    subscriptions = UserSubscriptions.query.filter_by(user_id = user_id).all()
    
    assert len(subscriptions) == 2
    assert subscriptions[1].subscription_status == 'subscribed'

    # teardown, delete subscription, grants, and user
    UserSubscriptions.query.filter_by(user_id = user_id).delete()
    CommunityManagerSubscriptionGrants.query.filter_by(user_id = test_client.staff_id).delete()
    User.query.filter_by(user_id = user_id).delete()
    test_client.db.session.commit()    

def test_get_subscriptions_granted(test_client, subscription_grants):
    response = test_client.get(
        f"/community-manager/subscriptions/grant",
        headers=test_client.staff_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
