NOTIFICATION_TYPES_COUNT = 20
FIRST_NOTIFICATION_TYPE = 'DoseSpot'
LAST_NOTIFICATION_TYPE = 'Health'

def test_get_notifications(test_client):
    response = test_client.get(
        '/lookup/notifications/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    # Check for correct response, correct length, and correct notification type for a few rows
    assert response.status_code == 200
    assert response.json['total_items'] == NOTIFICATION_TYPES_COUNT
    assert response.json['items'][0]['notification_type'] == FIRST_NOTIFICATION_TYPE
    assert response.json['items'][-1]['notification_type'] == LAST_NOTIFICATION_TYPE