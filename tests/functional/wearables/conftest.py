import uuid

import pytest

from odyssey.api.wearables.models import WearablesV2
from .data import blood_glucose_data_1, blood_glucose_data_2, BLOOD_GLUCOSE_WEARABLE, test_8100_data_past_week, \
    test_8100_data_week_to_month_ago, BLOOD_PRESSURE_WEARABLE


@pytest.fixture(scope='function')
def add_blood_glucose_data(test_client):
    """
    Add some mock wearable data for blood glucose calculation tests
    """
    test_client.mongo.db.wearables.insert_many([blood_glucose_data_1, blood_glucose_data_2])
    
    yield [blood_glucose_data_1, blood_glucose_data_2]

    del_query = {'user_id': test_client.client_id, 'wearable': BLOOD_GLUCOSE_WEARABLE}
    test_client.mongo.db.wearables.delete_many(del_query)


@pytest.fixture(scope='function')
def bp_data_fixture(test_client):
    test_8100_data_past_week['user_id'] = test_client.client_id
    test_8100_data_week_to_month_ago['user_id'] = test_client.client_id
    test_client.mongo.db.wearables.insert_many([test_8100_data_past_week, test_8100_data_week_to_month_ago])

    # w = WearablesV2(
    #     wearable=BLOOD_PRESSURE_WEARABLE,
    #     terra_user_id=uuid.uuid4(),
    #     user_id=test_client.client_id,
    # )
    # test_client.db.session.add(w)
    # test_client.db.session.commit()

    yield [test_8100_data_past_week, test_8100_data_week_to_month_ago]

    del_query = {'user_id': test_client.client_id, 'wearable': BLOOD_PRESSURE_WEARABLE}
    test_client.mongo.db.wearables.delete_many(del_query)

    # test_client.db.session.delete(w)
    # test_client.db.session.commit()
