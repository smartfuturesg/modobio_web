import requests

from flask import current_app
from terra.api.api_responses import TerraApiResponse

from odyssey.api.wearables.models import WearablesV2
from odyssey.integrations.terra import TerraClient


def test_store_data(test_client):
    # test the TerraClient() class instantiation
    tc = TerraClient()
    assert tc

    # pull terra id and api key
    dev_id = current_app.config['TERRA_DEV_ID']
    x_api_key = current_app.config['TERRA_API_KEY']

    # get basically a list of users from terra
    headers = {
        'dev-id': dev_id,
        'x-api-key': x_api_key,
    }
    response = requests.get(url='https://api.tryterra.co/v2/subscriptions', headers=headers).json()

    assert response

    # try to get the terra user id for someone that uses OURA
    terra_user_id = None

    for u in response['users']:
        if u['provider'] == 'OMRONUS':
            terra_user_id = u['user_id']
            break

    # check we got one
    assert terra_user_id is not None

    # build url for getting body for user
    url = 'https://api.tryterra.co/v2/body?user_id=' + str(terra_user_id)
    url += '&start_date=2022-04-01&end_date=2022-04-09&to_webhook=false&with_samples=true'

    # send terra the get request
    response = requests.get(url=url, headers=headers)

    # create a terra library object that can be passed into out own client
    terra_response = TerraApiResponse(resp=response, dtype='activity')

    # if there are no samples for this data, the metadata will be empty
    for data in terra_response.get_json()['data']:
        if data['metadata']['start_time'] is None:
            data['metadata'] = {
                'start_time': '2022-06-01T00:00:00Z',
                'end_time': '2022-06-02T00:00:00Z',
            }

    # we need to inject into Wearables
    user_wearable = WearablesV2(
        user_id=test_client.client_id,
        wearable='OURA',
        terra_user_id=terra_user_id,
    )
    test_client.db.session.add(user_wearable)
    test_client.db.session.commit()

    # track the current count in case someone does not clean up after themselves down the road
    before_mongo_count = test_client.mongo.db.wearables.count_documents({})

    # use the terra client store_data function which is the center point of our data intake
    tc.store_data(terra_response)

    # record the new document count for wearables collection
    after_mongo_count = test_client.mongo.db.wearables.count_documents({})

    # assert to check that store_data worked
    assert 0 <= before_mongo_count < after_mongo_count

    # clean up
    test_client.mongo.db.wearables.delete_many({
        'user_id': test_client.client_id
    })
    test_client.db.session.delete(user_wearable)
    test_client.db.session.commit()

    # check that we are back to where we started to try to keep idempotency
    assert test_client.mongo.db.wearables.count_documents({}) == before_mongo_count
