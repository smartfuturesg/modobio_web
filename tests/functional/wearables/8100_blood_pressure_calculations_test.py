import uuid

from odyssey.api.wearables.models import WearablesV2
from .data import BLOOD_PRESSURE_WEARABLE, test_8100_data_past_week, test_8100_data_week_to_month_ago


def test_blood_pressure_calculations_default_date_filters(test_client):
    # insert test data
    # I am not using the store_data function in the TerraClient 'tc', for now
    # Instead I am attempting to inject data in the format that function would upsert it in
    # This could need to be changed someday to use that function plus datetime now instead of hard coded test data
    # However, that would require a bit of work to figure out what exactly we pass to that function or refactoring tc
    test_8100_data_past_week['user_id'] = test_client.client_id
    test_8100_data_week_to_month_ago['user_id'] = test_client.client_id
    test_client.mongo.db.wearables.insert_many([test_8100_data_past_week, test_8100_data_week_to_month_ago])

    w = WearablesV2(
        wearable=BLOOD_PRESSURE_WEARABLE,
        terra_user_id=uuid.uuid4(),
        user_id=test_client.client_id,
    )
    test_client.db.session.add(w)
    test_client.db.session.commit()

    # call endpoint
    response = test_client.get(
        f'/v2/wearables/calculations/blood-pressure/variation/{test_client.client_id}/{BLOOD_PRESSURE_WEARABLE}',
        headers=test_client.staff_auth_header,
        content_type='application/json',
    )

    assert response.status_code == 200

    # clean up mongoDB
    del_query = {'user_id': test_client.client_id, 'wearable': BLOOD_PRESSURE_WEARABLE}
    test_client.mongo.db.wearables.delete_many(del_query)
