# from flask.json import dumps
# from odyssey.api.doctor.models import MedicalBloodPressures

# from .data import doctor_blood_pressures_data

# import pytest


# def test_post_1_blood_pressure_history(test_client):
#     response = test_client.post(
#         f"/doctor/bloodpressure/{test_client.client_id}/",
#         headers=test_client.client_auth_header,
#         data=dumps(doctor_blood_pressures_data),
#         content_type="application/json",
#     )

#     assert response.status_code == 201


# def test_post_blood_pressure_invalid_pulse(test_client):
#     # Change pulse value outside the acceptable range
#     doctor_blood_pressures_data["pulse"] = 0

#     response = test_client.post(
#         f"/doctor/bloodpressure/{test_client.client_id}/",
#         headers=test_client.client_auth_header,
#         data=dumps(doctor_blood_pressures_data),
#         content_type="application/json",
#     )

#     # Ensure that invalid pulse throws bad request
#     assert response.status_code == 400
#     del doctor_blood_pressures_data["pulse"]


# def test_get_1_blood_pressure_history(test_client):
#     response = test_client.get(
#         f"/doctor/bloodpressure/{test_client.client_id}/",
#         headers=test_client.client_auth_header,
#         content_type="application/json",
#     )

#     assert response.status_code == 200
#     assert len(response.json["items"]) == 1
#     assert response.json["total_items"] == 1


# def test_delete_blood_pressure(test_client):
#     response = test_client.delete(
#         f"/doctor/bloodpressure/{test_client.client_id}/?idx=1",
#         headers=test_client.client_auth_header,
#     )

#     assert response.status_code == 204

#     # send get request to ensure the result was deleted
#     response = test_client.get(
#         f"/doctor/bloodpressure/{test_client.client_id}/",
#         headers=test_client.client_auth_header,
#         content_type="application/json",
#     )

#     assert response.status_code == 200
#     assert len(response.json["items"]) == 0
#     assert response.json["total_items"] == 0


# def test_post_blood_pressure_sources(test_client):
#     # Test blood pressure reading sources
#     response = test_client.post(
#         f"/doctor/bloodpressure/{test_client.client_id}/",
#         headers=test_client.client_auth_header,
#         data=dumps(doctor_blood_pressures_data),
#         content_type="application/json",
#     )

#     assert response.status_code == 201
#     assert response.json["source"] == "manual"

#     doctor_blood_pressures_data["source"] = "device"
#     doctor_blood_pressures_data["device_name"] = "apple"
#     response = test_client.post(
#         f"/doctor/bloodpressure/{test_client.client_id}/",
#         headers=test_client.client_auth_header,
#         data=dumps(doctor_blood_pressures_data),
#         content_type="application/json",
#     )

#     assert response.status_code == 201
#     assert response.json["source"] == "device"
#     assert response.json["device_name"] == "apple"

#     # Cleanup
#     bps = MedicalBloodPressures.query.filter_by(user_id=test_client.client_id).all()
#     for bp in bps:
#         test_client.db.session.delete(bp)
#     test_client.db.session.commit()
#     del doctor_blood_pressures_data["source"]
#     del doctor_blood_pressures_data["device_name"]


# def test_post_blood_pressure_source_no_device_name(test_client):
#     doctor_blood_pressures_data["source"] = "device"
#     response = test_client.post(
#         f"/doctor/bloodpressure/{test_client.client_id}/",
#         headers=test_client.client_auth_header,
#         data=dumps(doctor_blood_pressures_data),
#         content_type="application/json",
#     )

#     # Ensure 400 is raised for not passing in device name with the source being a device
#     assert response.status_code == 400
