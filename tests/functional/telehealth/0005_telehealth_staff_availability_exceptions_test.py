from flask.json import dumps
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from odyssey import db
from odyssey.api.telehealth.models import TelehealthStaffAvailabilityExceptions, TelehealthStaffSettings
from odyssey.tasks.periodic import remove_expired_availability_exceptions
import pytest

from .data import telehealth_exceptions_post_data

current_date = datetime.now(timezone.utc).date()

#TODO Telehealth on the Shelf - all tests skipped - remove skip annotations when telehealth reactivated

@pytest.mark.skip(reason="Telehealth on the Shelf")
def test_post_staff_availability_exception(test_client):
    telehealth_exceptions_post_data["bad_data_1"][0]["exception_date"] = str(current_date)
    
    response = test_client.post(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        data=dumps(telehealth_exceptions_post_data["bad_data_1"]),
        content_type='application/json')

    #should error since the data gives an end time that is after the start time
    assert response.status_code == 400
    
    telehealth_exceptions_post_data["bad_data_2"][0]["exception_date"] = str(current_date + relativedelta(months=+6, days=+1))
        
    response = test_client.post(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        data=dumps(telehealth_exceptions_post_data["bad_data_2"]),
        content_type='application/json')

    #should error since the data gives exception date more than 6 months in the future
    assert response.status_code == 400
    
    telehealth_exceptions_post_data["bad_data_2"][0]["exception_date"] = str(current_date + relativedelta(days=-1))
        
    response = test_client.post(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        data=dumps(telehealth_exceptions_post_data["bad_data_2"]),
        content_type='application/json')

    #should error since the data gives exception date in the past
    assert response.status_code == 400
    
    telehealth_exceptions_post_data["good_data"][0]["exception_date"] = str(current_date)
    
    response = test_client.post(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        data=dumps(telehealth_exceptions_post_data["good_data"]),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['exceptions'][0]['exception_start_time'] == telehealth_exceptions_post_data["good_data"][0]['exception_start_time']
    assert response.json['exceptions'][0]['exception_end_time'] == telehealth_exceptions_post_data["good_data"][0]['exception_end_time']
    assert response.json['exceptions'][0]['is_busy'] == telehealth_exceptions_post_data["good_data"][0]['is_busy']
    assert response.json['exceptions'][0]['label'] == telehealth_exceptions_post_data["good_data"][0]['label']
    assert response.json['exceptions'][0]['exception_date'] == str(current_date)


@pytest.mark.skip(reason="Telehealth on the Shelf")
def test_get_staff_availability_exception(test_client):

    response = test_client.get(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert response.json[0]['exception_start_time'] == telehealth_exceptions_post_data["good_data"][0]['exception_start_time']
    assert response.json[0]['exception_end_time'] == telehealth_exceptions_post_data["good_data"][0]['exception_end_time']
    assert response.json[0]['is_busy'] == telehealth_exceptions_post_data["good_data"][0]['is_busy']
    assert response.json[0]['label'] == telehealth_exceptions_post_data["good_data"][0]['label']
    assert response.json[0]['exception_date'] == str(current_date)


@pytest.mark.skip(reason="Telehealth on the Shelf")
def test_delete_staff_availability_exception(test_client):

    response = test_client.delete(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        data=dumps([{'exception_id': 1}]),
        content_type='application/json')

    assert response.status_code == 204
    
    response = test_client.get(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        content_type='application/json')
    
    assert response.status_code == 200
    assert len(response.json) == 0


@pytest.mark.skip(reason="Telehealth on the Shelf")
def test_celery_delete_exceptions_task(test_client):
    
    telehealth_exceptions_post_data["good_data"][0]["exception_date"] = str(current_date)
    
    response = test_client.post(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        data=dumps(telehealth_exceptions_post_data["good_data"]),
        content_type='application/json')

    assert response.status_code == 201
    
    #check that GET now returns 1 exception
    response = test_client.get(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 1
    
    #manually run celery task
    remove_expired_availability_exceptions()
    
    #check that exception still exists since it's not after the date yet
    response = test_client.get(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 1
    
    #have to forcibly change the date since past dates can't be submitted
    exception = TelehealthStaffAvailabilityExceptions.query.filter_by(user_id=test_client.provider_id).one_or_none()
    
    exception.exception_date = str(current_date - relativedelta(days=1))
    db.session.commit()
    
    #manually run celery task
    remove_expired_availability_exceptions()
    
    response = test_client.get(
        f'/telehealth/settings/staff/availability/exceptions/{test_client.provider_id}/',
        headers=test_client.provider_auth_header,
        content_type='application/json')

    assert response.status_code == 200
    assert len(response.json) == 0