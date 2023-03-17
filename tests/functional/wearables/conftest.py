import pytest
import csv
from dateutil.parser import parse
import pytest

from .data import blood_glucose_data_1, blood_glucose_data_2, BLOOD_GLUCOSE_WEARABLE

@pytest.fixture(scope='function')
def add_blood_glucose_data(test_client):
    """
    Add some mock wearable data for blood glucose calculation tests
    """
    test_client.mongo.db.wearables.insert_many([blood_glucose_data_1, blood_glucose_data_2])
    
    yield [blood_glucose_data_1, blood_glucose_data_2]

    del_query = {'user_id': test_client.client_id, 'wearable': BLOOD_GLUCOSE_WEARABLE}
    test_client.mongo.db.wearables.delete_many(del_query)


@pytest.fixture(scope='module')
def add_cgm_data(test_client):
    """
    Read data from file and insert into mongodb wearables collection
    """
    # read data from file
    with open("tests/functional/wearables/cgm_14_day.csv", "r") as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)
        f.close()

    # loop through data and group by days
    # each document will represent a day of data
    cgm_samples = []
    cgm_sum = 0
    documents = []
    data_start_time = parse(csv_data[0]["timestamp"])
    data_end_time = parse(csv_data[-1]["timestamp"])

    for i, dat in enumerate(csv_data):
        if i > 0 and parse(dat["timestamp"]).time() < csv_data[i-1]["timestamp"].time():
            # complete the document and start new list of data points
            # come up with average
            avg = cgm_sum/len(cgm_samples)
            documents.append({
                "user_id": test_client.client_id,
                "wearable": BLOOD_GLUCOSE_WEARABLE,
                "timestamp": cgm_samples[0]["timestamp"],
                "data": {
                    "day_avg_blood_glucose_mg_per_dL": cgm_sum/len(cgm_samples),
                    "blood_glucose_samples": cgm_samples
                }
                }
            )
            dat["timestamp"] = parse(dat["timestamp"])
            cgm_samples = [dat]
            cgm_sum = float(dat["blood_glucose_mg_per_dL"])
        else:
            dat["timestamp"] = parse(dat["timestamp"])
            cgm_samples.append(dat)
            cgm_sum += float(dat["blood_glucose_mg_per_dL"])

    test_client.mongo.db.wearables.insert_many(documents)

    yield {"data_start_time": data_start_time, "data_end_time": data_end_time}

    del_query = {'user_id': test_client.client_id, 'wearable': BLOOD_GLUCOSE_WEARABLE}
    test_client.mongo.db.wearables.delete_many(del_query)
