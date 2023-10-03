from flask.json import dumps
from odyssey.api.doctor.models import MedicalBloodPressures

from .data import doctor_blood_pressures_data



def test_post_1_blood_pressure_history(test_client):
    response = test_client.post(
        f"/doctor/bloodpressure/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(doctor_blood_pressures_data),
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json.get("_id") 

    # now delete the entry using _id
    _id = response.json.get("_id")
    response = test_client.delete(
        f"/doctor/bloodpressure/{test_client.client_id}/?_id={_id}",
        headers=test_client.client_auth_header,
    )
    assert response.status_code == 200
    assert response.json.get("delete_ok")


def test_post_blood_pressure_invalid_pulse(test_client):
    # Change pulse value outside the acceptable range
    doctor_blood_pressures_data["pulse"] = 0

    response = test_client.post(
        f"/doctor/bloodpressure/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(doctor_blood_pressures_data),
        content_type="application/json",
    )

    # Ensure that invalid pulse throws bad request
    assert response.status_code == 400
    del doctor_blood_pressures_data["pulse"]


def test_post_blood_pressure_source_no_device_name(test_client):
    doctor_blood_pressures_data["source"] = "device"
    response = test_client.post(
        f"/doctor/bloodpressure/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        data=dumps(doctor_blood_pressures_data),
        content_type="application/json",
    )

    # Ensure 400 is raised for not passing in device name with the source being a device
    assert response.status_code == 400
