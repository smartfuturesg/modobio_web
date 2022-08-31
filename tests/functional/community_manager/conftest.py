from bdb import Breakpoint
import pytest

from odyssey import db
from odyssey.api.community_manager.models import CommunityManagerSubscriptionGrants
from odyssey.api.user.models import User

from tests.utils import login


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
