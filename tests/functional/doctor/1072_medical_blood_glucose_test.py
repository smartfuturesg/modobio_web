from flask.json import dumps
from odyssey.api.doctor.models import MedicalBloodTests
from .data import blood_glucose_post_data, blood_glucose_put_data


def test_post_blood_glucose(test_client):
    response = test_client.post(
        f"/doctor/blood-glucose/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(blood_glucose_post_data),
        content_type="application/json",
    )

    assert response.status_code == 201

    glucose_test = MedicalBloodTests.query.filter_by(
        test_id=response.json["test_id"]
    ).one_or_none()
    test_client.db.session.delete(glucose_test)
    test_client.db.session.commit()


def test_get_blood_glucose(test_client, blood_glucose):
    response = test_client.get(
        f"/doctor/blood-glucose/{test_client.client_id}/?test_id={blood_glucose[0].test_id}",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["date"] == "2023-01-01"
    assert response.json["notes"] == "Test notes"
    assert response.json["was_fasted"] == True
    assert len(response.json["results"]) == 2


def test_put_blood_glucose(test_client, blood_glucose):
    response = test_client.put(
        f"/doctor/blood-glucose/{test_client.client_id}/?test_id={blood_glucose[0].test_id}",
        headers=test_client.client_auth_header,
        data=dumps(blood_glucose_put_data),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert blood_glucose[0].notes == "Updated notes"
    assert blood_glucose[0].was_fasted == False
    assert blood_glucose[1].evaluation == "abnormal"
    assert blood_glucose[2].evaluation == "abnormal"


def test_delete_blood_glucose(test_client):
    response_1 = test_client.post(
        f"/doctor/blood-glucose/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(blood_glucose_post_data),
        content_type="application/json",
    )

    assert response_1.status_code == 201

    response_2 = test_client.delete(
        f'/doctor/blood-glucose/{test_client.client_id}/?test_id={response_1.json["test_id"]}',
        headers=test_client.client_auth_header,
    )

    assert response_2.status_code == 204

    glucose_test = MedicalBloodTests.query.filter_by(
        test_id=response_1.json["test_id"]
    ).one_or_none()

    assert glucose_test is None
