from flask.json import dumps

def test_get_default_health_metrics(test_client):
    response = test_client.get(
        '/lookup/default-health-metrics/',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == 30
