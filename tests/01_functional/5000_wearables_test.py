from datetime import datetime

from flask.json import dumps

from odyssey.models.staff import Staff
from odyssey.models.wearables import Wearables, WearablesFreeStyle

from tests.data import wearables_data, wearables_freestyle_data

def test_wearables_post(test_client, init_database):
    """
    GIVEN an API end point for wearable devices
    WHEN the '/wearables/<client id>' resource is requested (POST)
    THEN check the response is valid
    """
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    response = test_client.post(
        '/wearables/1/',
        headers=headers,
        data=dumps(wearables_data),
        content_type='application/json'
    )

    assert response.status_code == 201

    data = Wearables.query.filter_by(clientid=1).first()

    assert data
    assert data.has_freestyle
    assert data.has_oura
    assert not data.registered_oura

def test_wearables_get(test_client, init_database):
    """
    GIVEN an API end point for wearable devices
    WHEN the '/wearables/<client id>' resource is requested (GET)
    THEN check the response is valid
    """
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    response = test_client.get(
        '/wearables/1/',
        headers=headers
    )

    assert response.status_code == 200
    assert response.json == wearables_data

def test_wearables_put(test_client, init_database):
    """
    GIVEN an API end point for wearable devices
    WHEN the '/wearables/<client id>' resource is requested (PUT)
    THEN check the response is valid
    """
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    new_data = wearables_data.copy()
    new_data['has_oura'] = False

    response = test_client.put(
        '/wearables/1/',
        headers=headers,
        data=dumps(new_data),
        content_type='application/json'
    )

    assert response.status_code == 204

    data = Wearables.query.filter_by(clientid=1).first()

    assert data.has_freestyle
    assert not data.has_oura

def test_wearables_freestyle_activate_post(test_client, init_database):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/activate/<client id>' resource is requested (POST)
    THEN check the response is valid
    """
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    ts = wearables_freestyle_data['activation_timestamp']

    response = test_client.post(
        '/wearables/freestyle/activate/1/',
        headers=headers,
        data=dumps({'activation_timestamp': ts}),
        content_type='application/json'
    )

    assert response.status_code == 201

    data = WearablesFreeStyle.query.filter_by(clientid=1).first()

    assert data
    assert data.activation_timestamp == datetime.fromisoformat(ts)


def test_wearables_freestyle_activate_get(test_client, init_database):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/activate/<client id>' resource is requested (GET)
    THEN check the response is valid
    """
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}

    response = test_client.get(
        '/wearables/freestyle/activate/1/',
        headers=headers
    )

    assert response.status_code == 200
    ret = datetime.fromisoformat(response.json['activation_timestamp'])
    orig = datetime.fromisoformat(wearables_freestyle_data['activation_timestamp'])
    assert ret == orig

def test_wearables_freestyle_put(test_client, init_database):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/<client id>' resource is requested (PUT)
    THEN check the response is valid
    """
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    tss = [datetime.fromisoformat(d) for d in wearables_freestyle_data['timestamps']]

    response = test_client.put(
        '/wearables/freestyle/1/',
        headers=headers,
        data=dumps(wearables_freestyle_data),
        content_type='application/json'
    )

    assert response.status_code == 201

    data = WearablesFreeStyle.query.filter_by(clientid=1).first()

    assert data
    assert data.glucose == wearables_freestyle_data['glucose']
    assert data.timestamps == tss

def test_wearables_freestyle_get(test_client, init_database):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/<client id>' resource is requested (GET)
    THEN check the response is valid
    """
    staff = Staff.query.first()
    token = staff.get_token()
    headers = {'Authorization': f'Bearer {token}'}
    tss = [datetime.fromisoformat(d) for d in wearables_freestyle_data['timestamps']]

    response = test_client.get(
        '/wearables/freestyle/1/',
        headers=headers
    )

    assert response.status_code == 200
    assert response.json['glucose'] == wearables_freestyle_data['glucose']

    returned_dt = [datetime.fromisoformat(d) for d in response.json['timestamps']]
    orig_dt = [datetime.fromisoformat(d) for d in wearables_freestyle_data['timestamps']]
    assert all([ret == orig for ret, orig in zip(returned_dt, orig_dt)])
