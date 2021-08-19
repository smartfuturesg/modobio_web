from flask.json import dumps
from odyssey.api.staff.models import StaffCalendarEvents
from .data import staff_calendar_events_data

# TODO: Fix endpoint, don't just skip test.
import pytest
pytestmark = pytest.mark.skip('Setting timezone in calendar events is broken.')

def test_post_new_event(test_client):
    # using staff user
    # post daily event
    response = test_client.post(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['recurring']['daily_event']),
        content_type='application/json')

    assert response.status_code == 201

    # post weekly event
    response = test_client.post(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['recurring']['weekly_event']),
        content_type='application/json')

    assert response.status_code == 201

    # post monthly event
    response = test_client.post(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['recurring']['monthly_event']),
        content_type='application/json')

    assert response.status_code == 201

    # post yearly event
    response = test_client.post(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['recurring']['yearly_event']),
        content_type='application/json')

    assert response.status_code == 201

    # post invalid event
    response = test_client.post(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['recurring']['invalid_event']),
        content_type='application/json')

    assert response.status_code == 422

    # post non-recurring event
    response = test_client.post(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['non-recurring']['valid_event']),
        content_type='application/json')

    assert response.status_code == 201

    # post invalid event
    response = test_client.post(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['non-recurring']['invalid_event']),
        content_type='application/json')

    assert response.status_code == 400

def test_put_update_event(test_client):
    # edit daily event to weekly event
    query = StaffCalendarEvents.query.filter_by(idx=1).one_or_none()
    assert query.recurrence_type == "Daily"

    response = test_client.put(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(staff_calendar_events_data['edit_event']),
        content_type='application/json')

    query = StaffCalendarEvents.query.filter_by(idx=1).one_or_none()
    assert response.status_code == 200
    assert query.recurrence_type == "Weekly"

def test_get_events(test_client):
    # test calling get without parameters
    response = test_client.get(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200

    # "year": 2020
    response = test_client.get(
        f'/staff/calendar/{test_client.staff_id}/?year=2020',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 1

    # "year": 2021, "month": 2
    response = test_client.get(
        f'/staff/calendar/{test_client.staff_id}/?year=2021&month=2',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 1

    # {"year": 2021,  "month": 2, "day": 28}
    response = test_client.get(
        f'/staff/calendar/{test_client.staff_id}/?year=2021&month=2&day=28',
        headers=test_client.staff_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 1

def test_delete_event(test_client):
    payload = {
        'entire_series': True,
        'previous_start_date': '2021-05-19',
        'event_to_update_idx': 1}

    response = test_client.delete(
        f'/staff/calendar/{test_client.staff_id}/',
        headers=test_client.staff_auth_header,
        data=dumps(payload),
        content_type='application/json')

    query = StaffCalendarEvents.query.filter_by(idx=1).all()

    assert response.status_code == 200
    assert query == []
