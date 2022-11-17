from re import U
import pytest

from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.user.models import (
    User,
    UserPendingEmailVerifications,
    UserSubscriptions,
)
from odyssey.utils.misc import EmailVerification


@pytest.fixture(scope="function")
def subscription_grants(test_client):
    """Add subscription grants to the database."""
    test_client.db.session.query(CommunityManagerSubscriptionGrants).delete()

    grant_1 = CommunityManagerSubscriptionGrants(
        user_id=2,
        email="not_a_user@gmail.com",
        subscription_type_id=2,
        sponsor="Sponsoring Institution",
        activated=False,
    )

    grant_2 = CommunityManagerSubscriptionGrants(
        user_id=2,
        email=None,
        subscription_type_id=2,
        sponsor="Sponsoring Institution",
        activated=False,
    )

    test_client.db.session.add_all([grant_1, grant_2])
    test_client.db.session.commit()

    yield

    # delete all subscription grants
    test_client.db.session.query(CommunityManagerSubscriptionGrants).delete()
    test_client.db.session.commit()


@pytest.fixture(scope="function")
def unverified_user(test_client):
    """
    Creates a new client user that is not verified
    """
    user = User(
        email="unverified_test_user@modo.com",
        firstname="Testy",
        lastname="test",
        phone_number="1231231434",
        is_client=True,
        is_staff=False,
        was_staff=False,
    )
    test_client.db.session.add(user)
    test_client.db.session.flush()
    user_id = user.user_id
    user_subscription = UserSubscriptions(
        subscription_status="unsubscribed", is_staff=False, user_id=user.user_id
    )

    # create pending email verification in db
    email_verification_data = {
        "user_id": user_id,
        "token": "token",
        "code": 123,
        "email": user.email,
    }

    email_verification_data = EmailVerification().begin_email_verification(user, False)

    test_client.db.session.add(user_subscription)
    test_client.db.session.commit()

    yield user, email_verification_data

    User.query.filter_by(user_id=user_id).delete()
    UserSubscriptions.query.filter_by(user_id=user_id).delete()
    UserPendingEmailVerifications.query.filter_by(user_id=user_id).delete()
    CommunityManagerSubscriptionGrants.query.filter_by(
        subscription_grantee_user_id=user_id
    ).delete()
    test_client.db.session.commit()
