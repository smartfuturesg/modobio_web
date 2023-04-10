import requests
# import pytest

from flask import current_app
from terra.api.api_responses import TerraApiResponse

from odyssey.api.wearables.models import WearablesV2
from odyssey.integrations.terra import TerraClient


# @pytest.mark.skip('IN DEV')
def test_store_data(test_client):
    # test the TerraClient() class instantiation
    tc = TerraClient()
    assert tc

    # pull terra id and api key
    dev_id = current_app.config['TERRA_DEV_ID']
    x_api_key = current_app.config['TERRA_API_KEY']

    headers = {
        'dev-id': dev_id,
        'x-api-key': x_api_key,
    }

    response = requests.get(url='https://api.tryterra.co/v2/subscriptions', headers=headers).json()

    assert response

    terra_user_id = None

    for u in response['users']:
        if u['provider'] == 'OURA':
            terra_user_id = u['user_id']
            break

    assert terra_user_id is not None

    url = 'https://api.tryterra.co/v2/body?user_id=' + str(terra_user_id)
    url += '&start_date=2022-06-01&end_date=2022-06-27&to_webhook=false&with_samples=true'

    response = requests.get(url=url, headers=headers)

    terra_response = TerraApiResponse(resp=response, dtype='activity')

    user_wearable = WearablesV2(
        user_id=test_client.client_id,
        wearable='OURA',
        terra_user_id=terra_user_id,
    )
    test_client.db.session.add(user_wearable)
    test_client.db.session.commit()

    before_mongo_count = test_client.mongo.db.wearables.count_documents({})

    tc.store_data(terra_response)

    after_mongo_count = test_client.mongo.db.wearables.count_documents({})

    assert 0 <= before_mongo_count < after_mongo_count

    # clean up
    test_client.mongo.db.wearables.delete_many({
        'user_id': test_client.client_id
    })

    assert test_client.mongo.db.wearables.count_documents({}) == before_mongo_count

    test_client.db.session.delete(user_wearable)
    test_client.db.session.commit()
