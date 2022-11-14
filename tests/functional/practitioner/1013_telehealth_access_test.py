from flask.json import dumps
from odyssey.api.telehealth.models import TelehealthStaffSettings


def test_get_telehealth_activation(test_client, staff_telehealth_access):
    staff_settings = TelehealthStaffSettings.query.filter_by(user_id=test_client.staff_id).one_or_none()

    response = test_client.get(
        f'/practitioner/telehealth-activation/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        content_type='application/json')

    assert response.json['provider_telehealth_access'] == staff_settings.provider_telehealth_access
    assert response.status_code == 200

def test_update_telehealth_activation(test_client, staff_telehealth_access):
    staff_settings = TelehealthStaffSettings.query.filter_by(user_id=test_client.staff_id).one_or_none()

    previous_telehealth_access_flag = staff_settings.provider_telehealth_access

    #switch telehealth flag
    data = {"provider_telehealth_access" : not previous_telehealth_access_flag}
    response = test_client.put(
        f'/practitioner/telehealth-activation/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type='application/json')
    assert response.status_code == 200
    assert response.json['provider_telehealth_access'] !=  previous_telehealth_access_flag

    #Restore flag
    staff_settings.provider_telehealth_access = previous_telehealth_access_flag
    test_client.db.session.commit()
    assert staff_settings.provider_telehealth_access == previous_telehealth_access_flag

 