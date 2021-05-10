from datetime import datetime

from flask.json import dumps

from odyssey.api.wearables.models import Wearables, WearablesFreeStyle

from .data import (
    wearables_freestyle_data,
    wearables_freestyle_more_data,
    wearables_freestyle_combo_data,
    wearables_freestyle_empty_data,
    wearables_freestyle_unequal_data,
    wearables_freestyle_duplicate_data
)

def test_wearables_freestyle_activate_post(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/activate/<user_id>' resource is requested (POST)
    THEN check the response is valid
    """
    
    ts = wearables_freestyle_data['activation_timestamp']

    response = test_client.post(
        '/wearables/freestyle/activate/1/',
        headers=client_auth_header,
        data=dumps({'activation_timestamp': ts}),
        content_type='application/json'
    )

    assert response.status_code == 201

    data = WearablesFreeStyle.query.filter_by(user_id=1).first()

    assert data
    assert data.activation_timestamp == datetime.fromisoformat(ts)


def test_wearables_freestyle_activate_get(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/activate/<user_id>' resource is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get(
        '/wearables/freestyle/activate/1/',
        headers=client_auth_header
    )

    assert response.status_code == 200
    ret = datetime.fromisoformat(response.json['activation_timestamp'])
    orig = datetime.fromisoformat(wearables_freestyle_data['activation_timestamp'])
    assert ret == orig

def test_wearables_freestyle_patch(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/<user_id>' resource is requested (PATCH)
    THEN check the response is valid
    """

    tss = [datetime.fromisoformat(d) for d in wearables_freestyle_data['timestamps']]

    ### Add data
    response = test_client.patch(
        '/wearables/freestyle/1/',
        headers=client_auth_header,
        data=dumps(wearables_freestyle_data),
        content_type='application/json'
    )

    assert response.status_code == 204

    data = WearablesFreeStyle.query.filter_by(user_id=1).first()

    assert data
    assert data.glucose == wearables_freestyle_data['glucose']
    assert data.timestamps == tss

    ### Add data with some overlapping dates (previously added data)
    # Afterwards, data should look like wearables_freestyle_data_combo
    cur_len = len(data.timestamps)

    response = test_client.patch(
        '/wearables/freestyle/1/',
        headers=client_auth_header,
        data=dumps(wearables_freestyle_more_data),
        content_type='application/json'
    )
    
    assert response.status_code == 204
    
    init_database.session.commit()
    assert len(data.timestamps) == len(wearables_freestyle_combo_data['timestamps'])
    assert data.glucose == wearables_freestyle_combo_data['glucose']

    combo_dt = [datetime.fromisoformat(d) for d in wearables_freestyle_combo_data['timestamps']]
    assert all([ret == orig for ret, orig in zip(data.timestamps, combo_dt)])

    ### Add empty data set
    cur_len = len(data.timestamps)

    response = test_client.patch(
        '/wearables/freestyle/1/',
        headers=client_auth_header,
        data=dumps(wearables_freestyle_empty_data),
        content_type='application/json'
    )

    assert response.status_code == 204

    init_database.session.commit()
    assert len(data.timestamps) == cur_len

    ### Add data with unequal lengths
    response = test_client.patch(
        '/wearables/freestyle/1/',
        headers=client_auth_header,
        data=dumps(wearables_freestyle_unequal_data),
        content_type='application/json'
    )

    assert response.status_code == 400
    assert 'not equal length' in response.json['message']
    init_database.session.commit()
    assert len(data.timestamps) == cur_len

    ### Add data with duplicate dates
    response = test_client.patch(
        '/wearables/freestyle/1/',
        headers=client_auth_header,
        data=dumps(wearables_freestyle_duplicate_data),
        content_type='application/json'
    )

    assert response.status_code == 400
    assert 'Duplicate timestamps' in response.json['message']
    init_database.session.commit()
    assert len(data.timestamps) == cur_len    

def test_wearables_freestyle_get(test_client, init_database, client_auth_header):
    """
    GIVEN an API end point for the FreeStyle Libre CGM
    WHEN the '/wearables/freestyle/<user_id>' resource is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get(
        '/wearables/freestyle/1/',
        headers=client_auth_header
    )

    assert response.status_code == 200
    assert response.json['glucose'] == wearables_freestyle_combo_data['glucose']

    returned_dt = [datetime.fromisoformat(d) for d in response.json['timestamps']]
    orig_dt = [datetime.fromisoformat(d) for d in wearables_freestyle_combo_data['timestamps']]
    assert all([ret == orig for ret, orig in zip(returned_dt, orig_dt)])
