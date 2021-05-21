from flask.json import dumps
from odyssey.api.staff.models import StaffCalendarEvents
from odyssey import db
from .data import staff_calendar_events_data

def test_post_new_event(test_client, init_database, staff_auth_header):
    """
    GIVEN an api endpoint for creating new calendar events
    WHEN the '/staff/calendar/:user_id/' resource is requested 
    THEN an event is created, check the response is valid
    """
    #using user_id 2 for staff user
    #post daily event
    response = test_client.post('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['recurring']['daily_event']),
                                content_type='application/json')

    assert response.status_code == 201

    #post weekly event
    response = test_client.post('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['recurring']['weekly_event']),
                                content_type='application/json')

    assert response.status_code == 201

    #post monthly event
    response = test_client.post('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['recurring']['monthly_event']),
                                content_type='application/json')

    assert response.status_code == 201

    #post yearly event
    response = test_client.post('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['recurring']['yearly_event']),
                                content_type='application/json')

    assert response.status_code == 201

    #post invalid event
    response = test_client.post('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['recurring']['invalid_event']),
                                content_type='application/json')
    
    assert response.status_code == 422

    #post non-recurring event
    response = test_client.post('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['non-recurring']['valid_event']),
                                content_type='application/json')
    
    assert response.status_code == 201

    #post invalid event
    response = test_client.post('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['non-recurring']['invalid_event']),
                                content_type='application/json')
    
    assert response.status_code == 400


def test_put_update_event(test_client, init_database, staff_auth_header):
    """
    GIVEN an api endpoint for updating calendar events
    WHEN the '/staff/calendar/:user_id/' resource is requested 
    THEN an event is modified, check the response is valid
    """
    #edit daily event to weekly event
    query = StaffCalendarEvents.query.filter_by(idx=1).one_or_none()
    assert query.recurrence_type == "Daily"

    response = test_client.put('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(staff_calendar_events_data['edit_event']),
                                content_type='application/json')

    query = StaffCalendarEvents.query.filter_by(idx=1).one_or_none()
    assert response.status_code == 200
    assert query.recurrence_type == "Weekly"

def test_get_events(test_client, init_database, staff_auth_header):
    """
    GIVEN an api endpoint for viewing calendar events
    WHEN the '/staff/calendar/:user_id/' resource is requested 
    THEN an events are returned, check the response is valid
    """
    #test calling get without parameters
    payload = {}
    response = test_client.get('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(payload),
                                content_type='application/json')
    
    assert response.status_code == 200
    
    payload = {"year": 2020}
    response = test_client.get('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(payload),
                                content_type='application/json')
    
    assert response.status_code == 200
    assert len(response.json) == 1

    payload = {"year": 2021,
               "month": 2}
    response = test_client.get('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(payload),
                                content_type='application/json')
    
    assert response.status_code == 200
    assert len(response.json) == 1

    payload = {"year": 2021,
               "month": 2,
               "day": 28}
    response = test_client.get('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(payload),
                                content_type='application/json')
    
    assert response.status_code == 200
    assert len(response.json) == 1

def test_delete_event(test_client, init_database, staff_auth_header):
    """
    GIVEN an api endpoint for deleting calendar events
    WHEN the '/staff/calendar/:user_id/' resource is requested 
    THEN an event or series of events get deleted, check the response is valid
    """
    payload = {"entire_series": True,
               "previous_start_date": "2021-05-19",
               "event_to_update_idx": 1}
    response = test_client.delete('/staff/calendar/2/',
                                headers=staff_auth_header,
                                data=dumps(payload),
                                content_type='application/json')
    query = StaffCalendarEvents.query.filter_by(idx=1).all()
    
    assert response.status_code == 200
    assert query == []
