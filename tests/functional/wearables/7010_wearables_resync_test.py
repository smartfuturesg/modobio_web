from datetime import datetime

from odyssey.api.user.models import User
from odyssey.api.wearables.models import WearablesV2
from tests.utils import login


def test_wearables_resync(test_client):
    """Test resync endpoint as client and then as community manager"""
    current_time = datetime.now()

    # bring up the oura ring user
    oura_user = User.query.filter_by(email="oura@modobio.com").one_or_none()

    # set last_sync_date to now so that the test doesnt send a request to terra
    wearable = WearablesV2.query.filter_by(user_id=oura_user.user_id).one_or_none()
    wearable.last_sync_date = current_time
    test_client.db.session.commit()

    # log the user in
    oura_client_login = login(test_client, oura_user, password="123")

    response = test_client.get(
        f"/v2/wearables/sync/{oura_user.user_id}",
        headers=oura_client_login,
        content_type="application/json",
    )

    # check that last_sync_date was not updated
    wearable = WearablesV2.query.filter_by(user_id=oura_user.user_id).one_or_none()

    assert wearable.last_sync_date == current_time
    assert response.status_code == 200

    # test again but as staff holding the community_manager role
    response = test_client.get(
        f"/v2/wearables/sync/{oura_user.user_id}",
        headers=test_client.staff_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200

    # test again but as provider. Not allowed
    response = test_client.get(
        f"/v2/wearables/sync/{oura_user.user_id}",
        headers=test_client.provider_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 401
