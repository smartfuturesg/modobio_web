import pytest

from .data import blood_glucose_data_1, blood_glucose_data_2, BLOOD_GLUCOSE_WEARABLE, blood_pressure_data_1, blood_pressure_data_2, BLOOD_PRESSURE_WEARABLE

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