from datetime import datetime, timedelta
import json

def test_get_fitbit_document_no_query_params(test_client, fitbit_data):
    #With no query params, the default date range is one week ago from today. 
    #Should return 1 document 
    response = test_client.get(
        f'/v2/wearables/{test_client.client_id}/FITBIT',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    
    data = response.json
    
    assert len(data['results']) == 1
    assert data['results'][0]['user_id'] == test_client.client_id
    assert data['results'][0]['wearable'] == 'FITBIT'
    assert 'Activity' in data['results'][0]['data']

def test_get_fitbit_document_with_start_date(test_client, fitbit_data):

    start_date = datetime.utcnow() - timedelta(weeks=3)
    response = test_client.get(
        f'/v2/wearables/{test_client.client_id}/FITBIT?start_date={start_date.isoformat()}',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    
    data = response.json

    assert len(data['results']) == 2
    assert data['results'][0]['user_id'] == data['results'][1]['user_id'] == test_client.client_id
    assert data['results'][0]['wearable'] == data['results'][1]['wearable'] == 'FITBIT'
    assert 'Activity' in data['results'][0]['data']
    assert 'Athlete' in data['results'][1]['data']

def test_get_fitbit_document_with_start_and_end_date(test_client, fitbit_data):

    #Make start and end date a range where only 1 document exsits
    start_date = datetime.utcnow() - timedelta(weeks=3)
    end_date = datetime.utcnow() - timedelta(weeks=2)
    response = test_client.get(
        f'/v2/wearables/{test_client.client_id}/FITBIT?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    
    data = response.json

    assert len(data['results']) == 1
    assert 'Athlete' in data['results'][0]['data']

    #Change end date to before any documents were created. Should return zero documents. 
    end_date = datetime.utcnow() - timedelta(weeks=2.5)
    response = test_client.get(
        f'/v2/wearables/{test_client.client_id}/FITBIT?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    
    data = response.json

    assert len(data['results']) == 0

def test_get_fitbit_document_with_specified_fields(test_client, fitbit_data):

    #Specify that we want the heart_rate_data from data.Activity
    response = test_client.get(
        f'/v2/wearables/{test_client.client_id}/FITBIT?query_specification=data.Activity.heart_rate_data',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    
    data = response.json

    #'data' should only have the one specified field
    assert len(data['results'][0]['data']['Activity'].keys()) == 1
    assert 'heart_rate_data' in data['results'][0]['data']['Activity']

def test_get_fitbit_document_with_two_specified_fields(test_client, fitbit_data):

    #Specify that we want the calories_data and heart_rate_data from data.Activity
    response = test_client.get(
        f'/v2/wearables/{test_client.client_id}/'
        f'FITBIT?query_specification=data.Activity.heart_rate_data&query_specification=data.Activity.calories_data',
        headers=test_client.staff_auth_header,
        content_type='application/json')
    
    data = response.json

    #'data' should only have the two specified fields
    assert len(data['results'][0]['data']['Activity'].keys()) == 2
    assert 'heart_rate_data' in data['results'][0]['data']['Activity']
    assert 'calories_data' in data['results'][0]['data']['Activity']