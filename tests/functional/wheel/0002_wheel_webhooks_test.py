import pytest
from datetime import datetime, timedelta
import random
from dateutil import tz
import pytest

import pytest
from sqlalchemy import select
from odyssey.api.notifications.models import Notifications
from odyssey.api.telehealth.models import TelehealthBookingStatus

from odyssey.integrations.wheel import Wheel
from odyssey.tasks.tasks import process_wheel_webhooks

# @pytest.mark.skip
def test_wheel_webhooks(test_client, wheel_telehealth_booking):
    """
    Webhooks sent from wheel all have the same format:

    { 
    “event”: <designates the purpose of this request>, 
    “clinician_id”: <wheel id of the clinician>, 
    “clinician_email”: <email of clinician, will be the same as their modobio account>, 
    “consult_id”: <modobio generated UUID for the consultation> 
    }
    """
    global booking
    booking = wheel_telehealth_booking

    payload = {
        'clinician_id': 'a98f3ccb-093c-4831-a612-8d403589ae9f', 
        'clinician_email': 'wheelclinicianmd1@modobio.com', 
        'consult_id': booking.external_booking_id,
        'patient_id': 'TC12JASDFF12',
        'modobio_meta': {
            'processed': False,
            'acknowledged': False,
            'request_timestamp': datetime.now()
        }
    }


    ###
    # Event: 'consult.unassigned',  'clinician.no_show', 'clinician.unavailable', 'consult.voided'
    # All have the same routine to cancel the booking due to either the practitioenr or wheel cancelling
    # Expected actions:
    #   - update telehealth booking status
    #   - make an entry into telehealth booking status table
    #   - notification set to the client
    ###

    payload['event'] = 'consult.unassigned'

    process_wheel_webhooks(payload)

    # check for notification
    # check that booking status was set
    # check entry in TelehealthBookingStatus table
    booking_stauts_latest = test_client.db.session.execute(
        select(TelehealthBookingStatus).where(TelehealthBookingStatus.booking_id == booking.idx)).scalars().all()[-1]
    
    latest_notification = test_client.db.session.execute(
        select(Notifications).where(Notifications.user_id == booking.client_user_id)).scalars().all()[-1]

    
    assert booking.status == 'Canceled'
    assert booking_stauts_latest.status == 'Canceled'
    assert latest_notification.notification_type_id == 3

    ###
    # Event: 'assignment.accepted',  
    # Expected actions:
    #   - update telehealth booking status
    #   - make an entry into telehealth booking status table
    # 
    ###
    payload['event'] = 'assignment.accepted'

    process_wheel_webhooks(payload)

    booking_stauts_latest = test_client.db.session.execute(
        select(TelehealthBookingStatus).where(TelehealthBookingStatus.booking_id == booking.idx)).scalars().all()[-1]

    assert booking.status == 'Document Review'
    assert booking_stauts_latest.status == 'Document Review'

    ###
    # Event: 'patient.no_show',  
    # Expected actions:
    #   - update telehealth booking status
    #   - make an entry into telehealth booking status table
    #   - notify client that their appointment has been completed
    ###
    payload['event'] = 'patient.no_show'

    process_wheel_webhooks(payload)

    booking_stauts_latest = test_client.db.session.execute(
        select(TelehealthBookingStatus).where(TelehealthBookingStatus.booking_id == booking.idx)).scalars().all()[-1]

    latest_notification = test_client.db.session.execute(
        select(Notifications).where(Notifications.user_id == booking.client_user_id)).scalars().all()[-1]

    assert booking.status == 'Completed'
    assert booking_stauts_latest.status == 'Completed'
    assert latest_notification.notification_type_id == 3


    ###
    # Event: 'consult.assigned',  
    # Expected actions:
    #   - none currently
    ###
    payload['event'] = 'consult.assigned'

    process_wheel_webhooks(payload)

    
    assert True


















