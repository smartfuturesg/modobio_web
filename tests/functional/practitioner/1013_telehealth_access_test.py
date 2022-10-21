from flask.json import dumps
from odyssey.api.user.models import User


def test_get_telehealth_activation(test_client):
    response = test_client.get(
        f'/practitioner/telehealth-activation/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.json['provider_telehealth_access'] == False
    assert response.status_code == 200

def test_update_telehealth_activation(test_client):
    data = {"provider_telehealth_access" : True}
    response = test_client.put(
        f'/practitioner/telehealth-activation/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type='application/json')
    assert response.status_code == 200
    assert response.json['provider_telehealth_access'] == True

    user = User.query.filter_by(user_id=test_client.staff_id).one_or_none()
    assert user.provider_telehealth_access == True

    #set flag back to false
    user.provider_telehealth_access = False
    test_client.db.session.commit()