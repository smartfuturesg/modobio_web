from urllib import response
from flask.json import dumps
from odyssey.api.practitioner.models import PractitionerCredentials

def test_verify_credentials(test_client):
    cred = PractitionerCredentials.query.filter_by(user_id=test_client.staff.user_id).first()
    cred.status = 'Pending Verification'
    test_client.db.session.commit()

    #assert credentails object has been updated
    assert cred.status == 'Pending Verification'

    data = {
        "user_id": test_client.staff.user_id,
        "status": "Verified",
        "idx": cred.idx
    }

    response = test_client.put(
        f"/community-manager/verify-credentials",
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type="application/json",
    )

    # assert credentials object has been verified
    assert response.json['status'] == 'Verified'
    assert cred.status == 'Verified'
    assert response.status_code == 200



def test_verify_credentials_bad_status(test_client):
    cred = PractitionerCredentials.query.filter_by(user_id=test_client.staff.user_id).first()
    cred.status = 'Pending Verification'
    test_client.db.session.commit()

    #assert credentails object has been updated
    assert cred.status == 'Pending Verification'

    data = {
        "user_id": test_client.staff.user_id,
        "status": "invalid_status",
        "idx": cred.idx
    }

    response = test_client.put(
        f"/community-manager/verify-credentials",
        headers=test_client.staff_auth_header,
        data=dumps(data),
        content_type="application/json",
    )   

    assert response.status_code == 400