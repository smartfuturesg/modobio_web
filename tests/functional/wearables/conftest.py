import pytest

from .data import blood_glucose_data_1, blood_glucose_data_2, BLOOD_GLUCOSE_WEARABLE

@pytest.fixture(scope='function')
def add_blood_glucose_data(test_client):
    """
    Add some mock wearable data for blood glucose calculation tests
    """
    test_client.mongo.db.wearables.insert_many([blood_glucose_data_1, blood_glucose_data_2])
    
    yield [blood_glucose_data_1, blood_glucose_data_2]

    del_query = {'user_id': test_client.client_id, 'wearable': 'FREESTYLELIBRE'}
    test_client.mongo.db.wearables.delete_many(del_query)