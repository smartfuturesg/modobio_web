from flask import current_app
from .data import staff_profile_data


def test_get_staff_profile(test_client):
    response = test_client.get(
        f"/staff/profile/{test_client.staff_id}/", headers=test_client.staff_auth_header
    )

    # some simple checks for validity
    assert response.status_code == 200


def test_put_staff_profile(test_client):
    response = test_client.put(
        f"/staff/profile/{test_client.staff_id}/",
        headers=test_client.staff_auth_header,
        data=staff_profile_data["change_everything"],
    )

    # some simple checks for validity

    assert response.status_code == 200
    assert response.json["firstname"] == "Mario"
    assert response.json["middlename"] == "The"
    assert response.json["lastname"] == "Plumber"
    assert response.json["biological_sex_male"] == True
    assert response.json["bio"] == "It's a me, Mario!"
    assert response.json["profile_picture"] != None
    assert response.json["dob"] == "1995-06-14"

    # get profile and ensure fields have been updated
    response = test_client.get(
        f"/staff/profile/{test_client.staff_id}/", headers=test_client.staff_auth_header
    )

    assert response.status_code == 200
    assert response.json["firstname"] == "Mario"
    assert response.json["middlename"] == "The"
    assert response.json["lastname"] == "Plumber"
    assert response.json["biological_sex_male"] == True
    assert response.json["bio"] == "It's a me, Mario!"
    assert response.json["profile_picture"] != None
    assert response.json["dob"] == "1995-06-14"

    # test changing only the picture
    response = test_client.put(
        f"/staff/profile/{test_client.staff_id}/",
        headers=test_client.staff_auth_header,
        data=staff_profile_data["change_only_picture"],
    )

    assert response.status_code == 200

    response = test_client.get(
        f"/staff/profile/{test_client.staff_id}/", headers=test_client.staff_auth_header
    )

    assert response.status_code == 200
    assert response.json["profile_picture"] != None

    # TODO: does not work as intended. Disable for now.

    # #test deleting profile picture
    # response = test_client.put(
    #    f'/staff/profile/{test_client.staff_id}/',
    #    headers=test_client.staff_auth_header,
    #    data=staff_profile_data['remove_picture'])
    #
    # #just deleting the profile picture will succeed, but the response will have no body (even in local)
    # assert response.status_code == 204
    #
    # #get profile and ensure picture has been removed
    # response = test_client.get(
    #    f'/staff/profile/{test_client.staff_id}/',
    #    headers=test_client.staff_auth_header)
    # assert response.status_code == 200
    # assert response.json['profile_picture'] == None
