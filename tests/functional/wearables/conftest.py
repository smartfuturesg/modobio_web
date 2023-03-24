import pytest

from .data import (
    blood_glucose_data_1,
    blood_glucose_data_2,
    BLOOD_GLUCOSE_WEARABLE,
    wearables_fitbit_data_1,
    wearables_fitbit_data_2,
    test_8100_data_past_week,
    test_8100_data_week_to_month_ago,
    BLOOD_PRESSURE_WEARABLE,
    blood_pressure_data_1, 
    blood_pressure_data_2,
)


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
def add_blood_pressure_data(test_client):
    """
    Add mock wearable data for blood pressure calculation tests
    """
    test_client.mongo.db.wearables.insert_many([blood_pressure_data_1, blood_pressure_data_2])

    yield [blood_pressure_data_1, blood_pressure_data_2]

    del_query = {'user_id': test_client.client_id, 'wearable': BLOOD_PRESSURE_WEARABLE}
    test_client.mongo.db.wearables.delete_many(del_query)

@pytest.fixture(scope='function')
def fitbit_data(test_client):
    """
    Adds test fitbit data
    """
    test_client.mongo.db.wearables.insert_many([wearables_fitbit_data_1, wearables_fitbit_data_2])

    yield wearables_fitbit_data_1, wearables_fitbit_data_2

    query = {'user_id': test_client.client_id, 'wearable': 'FITBIT'}
    test_client.mongo.db.wearables.delete_many(query)


@pytest.fixture(scope='function')
def bp_data_fixture(test_client):
    test_8100_data_past_week['user_id'] = test_client.client_id
    test_8100_data_week_to_month_ago['user_id'] = test_client.client_id
    test_client.mongo.db.wearables.insert_many([test_8100_data_past_week, test_8100_data_week_to_month_ago])

    yield [test_8100_data_past_week, test_8100_data_week_to_month_ago]

    del_query = {'user_id': test_client.client_id, 'wearable': BLOOD_PRESSURE_WEARABLE}
    test_client.mongo.db.wearables.delete_many(del_query)
