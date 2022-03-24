def test_get_lookup_visit_reasons_all(test_client):
    response = test_client.get(
    '/lookup/visit-reasons/',
    headers=test_client.client_auth_header,
    content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == len(response.json['items'])
    assert response.json['total_items'] == 107


def test_get_lookup_visit_reasons_bad_role(test_client):
    response = test_client.get(
        '/lookup/visit-reasons/?role=badRole',
        headers=test_client.client_auth_header,
        content_type='application/json')

    assert response.status_code == 400


def test_get_lookup_visit_reasons_dietitian(test_client):
    response = test_client.get(
    '/lookup/visit-reasons/?role=dietitian',
    headers=test_client.client_auth_header,
    content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == len(response.json['items'])
    assert response.json['total_items'] == 26


def test_get_lookup_visit_reasons_medical_doctor(test_client):
    response = test_client.get(
    '/lookup/visit-reasons/?role=medical_doctor',
    headers=test_client.client_auth_header,
    content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == len(response.json['items'])
    assert response.json['total_items'] == 34


def test_get_lookup_visit_reasons_trainer(test_client):
    response = test_client.get(
    '/lookup/visit-reasons/?role=trainer',
    headers=test_client.client_auth_header,
    content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == len(response.json['items'])
    assert response.json['total_items'] == 23


def test_get_lookup_visit_reasons_therapist(test_client):
    response = test_client.get(
    '/lookup/visit-reasons/?role=therapist',
    headers=test_client.client_auth_header,
    content_type='application/json')

    assert response.status_code == 200
    assert response.json['total_items'] == len(response.json['items'])
    assert response.json['total_items'] == 24
    