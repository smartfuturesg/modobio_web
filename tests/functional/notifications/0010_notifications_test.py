from flask.json import dumps
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from odyssey import db
from odyssey.api.notifications.models import Notifications
from odyssey.tasks.periodic import remove_past_notifications
from odyssey.utils.misc import create_notification

from .data import notification_type, notification_update


current_date = datetime.now(timezone.utc).date()

def test_notifications_get(test_client):
        notification = {
            'user_id': test_client.client_id,
            'title': 'A nice title',
            'content': 'You have Spam!',
            'severity_id': 3,
            'read': False,
            'deleted': False,
            'notification_type_id': 1,
            'persona_type': 'Client'
        }
    
        obj = Notifications(**notification)
        
        db.session.add(obj)
        db.session.commit()
    
        response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 1

        notif = response.json[0]
        assert notif.get('title') == notification['title']
        assert notif.get('content') == notification['content']
        assert notif.get('read') == notification['read']
        assert notif.get('deleted') == notification['deleted']
        assert notif.get('notification_type') == notification_type
        assert notif.get('persona_type') == notification['persona_type']


def test_notifications_put(test_client):
        _notification = Notifications.query.filter_by(user_id = test_client.client_id).first()
        response = test_client.put(
            f'/notifications/{test_client.client_id}/{_notification.notification_id}/',
            headers=test_client.client_auth_header,
            data=dumps(notification_update),
            content_type='application/json')

        assert response.status_code == 200

        # No output from PUT, check again.
        response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

        assert response.status_code == 200
        assert type(response.json) == list
        assert len(response.json) == 1

        notif = response.json[0]
        # Unchanged
        assert notif.get('title') == 'A nice title'
        assert notif.get('content') == 'You have Spam!'
        assert notif.get('notification_type') == notification_type
        assert notif.get('persona_type') == 'Client'

        # Changed
        assert notif.get('read') == notification_update['read']
        assert notif.get('deleted') == notification_update['deleted']


def test_remove_past_notifications_deleted_flag(test_client):
    # First check that a notification is there and the deleted flag is set to True
    response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

    notif = response.json[0]

    assert response.status_code == 200
    assert type(response.json) == list
    assert len(response.json) == 1
    assert notif.get('deleted') == True

    # Run the code to remove past notifications
    remove_past_notifications()

    # Now make sure that the notification was removed
    response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

    assert response.status_code == 200
    assert type(response.json) == list
    assert len(response.json) == 0


def test_remove_past_notifications_expires_timestamp(test_client):

    create_notification(
        test_client.client_id,
        3,
        1,
        'A nice title',
        'You have Spam!',
        'Client',
        str(current_date - relativedelta(days=1)) # Set the notification to be expired
    )
    db.session.commit()

    # First check that a notification is there
    response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

    assert response.status_code == 200
    assert type(response.json) == list
    assert len(response.json) == 1

    # Run the code to remove past notifications
    remove_past_notifications()

    # Now make sure that the notification was removed
    response = test_client.get(
            f'/notifications/{test_client.client_id}/',
            headers=test_client.client_auth_header,
            content_type='application/json')

    assert response.status_code == 200
    assert type(response.json) == list
    assert len(response.json) == 0
