import pytest

from .data import blood_glucose_data_1, blood_glucose_data_2, BLOOD_GLUCOSE_WEARABLE, wearables_fitbit_data_1, wearables_fitbit_data_2

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
def fitbit_data(test_client):
    """
    Adds test fitbit data
    """
    test_client.mongo.db.wearables.insert_many([wearables_fitbit_data_1, wearables_fitbit_data_2])

    yield wearables_fitbit_data_1, wearables_fitbit_data_2

    query = {'user_id': test_client.client_id, 'wearable': 'FITBIT'}
    test_client.mongo.db.wearables.delete_many(query)