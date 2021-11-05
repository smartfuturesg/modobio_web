

def test_get_oura_data(test_client):
    """
    Testing the wearables/data GET endpoint for retrieving oura data

    All possible date specifications are attempted:
        - both start and end date provided: return data for date range
        - only start or end date specified: return start_date + 2 weeks OR end_date - 2 weeks
        - no dates specified: return last 2 weeks of data
    """

    client_user_id = 22
    # date range specified
    response = test_client.get(
        f'/wearables/data/oura/{client_user_id}/?start_date=2021-04-05&end_date=2021-04-10',
        headers=test_client.client_auth_header,
        content_type='application/json')
    breakpoint()
    assert response.status_code == 200
    
    # only start date specified
    response = test_client.get(
        f'/wearables/data/oura/{client_user_id}/?start_date=2021-10-05',
        headers=test_client.client_auth_header,
        content_type='application/json')
    assert response.status_code == 200
    
    # only end date specified
    response = test_client.get(
        f'/wearables/data/oura/{client_user_id}/?end_date=2021-10-15',
        headers=test_client.client_auth_header,
        content_type='application/json')
    assert response.status_code == 200

    # no date range specified
    response = test_client.get(
        f'/wearables/data/oura/{client_user_id}/',
        headers=test_client.client_auth_header,
        content_type='application/json')
    assert response.status_code == 200

    # wrong format dates
    response = test_client.get(
        f'/wearables/data/oura/{client_user_id}/?start_date=December&end_date=21-10-15',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 400


def test_get_applewatch_data(test_client):
    """
    Testing the wearables/data GET endpoint for retrieving applewatch data

    """
    client_user_id = 35
    # date range specified
    response = test_client.get(
        f'/wearables/data/applewatch/{client_user_id}/?start_date=2020-08-27&end_date=2021-12-02',
        headers=test_client.client_auth_header,
        content_type='application/json')
    assert response.status_code == 200

def test_get_fitbit_data(test_client):
    """
    Testing the wearables/data GET endpoint for retrieving fitbit data

    """
    client_user_id = 17
    # date range specified
    response = test_client.get(
        f'/wearables/data/fitbit/{client_user_id}/?start_date=2021-08-27&end_date=2021-08-30',
        headers=test_client.client_auth_header,
        content_type='application/json')
    assert response.status_code == 200
    
 

