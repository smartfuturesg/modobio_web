from flask.json import dumps
from odyssey.api.provider.models import ProviderCredentials

def test_verify_credentials(test_client):
    cred = ProviderCredentials.query.filter_by(user_id=test_client.provider.user_id).first()
    cred.status = 'Pending Verification'
    test_client.db.session.commit()

    #assert credentials object has been updated
    assert cred.status == 'Pending Verification'

    data = {
        "user_id": test_client.provider.user_id,
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
    cred = ProviderCredentials.query.filter_by(user_id=test_client.provider.user_id).first()
    cred.status = 'Pending Verification'
    test_client.db.session.commit()

    #assert credentials object has been updated
    assert cred.status == 'Pending Verification'

    #status is invalid
    data = {
        "user_id": test_client.provider.user_id,
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