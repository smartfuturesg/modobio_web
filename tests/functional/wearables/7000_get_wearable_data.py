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

def test_get_fitbit_data(test_client):


    client_user_id = 22
    # date range specified
    response = test_client.get(
        f'/wearables/data/fitbit/{client_user_id}/?start_date=2021-10-05&end_date=2021-10-15',
        headers=test_client.client_auth_header,
        content_type='application/json')
    
    # no date range specified
    response = test_client.get(
        f'/wearables/data/fitbit/{client_user_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 201

