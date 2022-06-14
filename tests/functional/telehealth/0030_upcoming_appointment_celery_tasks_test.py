from sqlalchemy import or_, select
from odyssey.api.client.models import ClientClinicalCareTeamAuthorizations
from odyssey.api.lookup.models import LookupClinicalCareTeamResources
from odyssey.api.notifications.models import Notifications

from odyssey.tasks.periodic import deploy_upcoming_appointment_tasks
from odyssey.tasks.tasks import upcoming_appointment_notification_2hr, upcoming_appointment_care_team_permissions

def test_upcoming_bookings_scan(test_client, upcoming_bookings):
    """
        To test the upcoming bookings scan we have to
    
        1) create at least 1 booking scheduled within the next 2 hours (done in a fixture)
        2) create at least 1 booking scheduled outside the next 2 hours (done in a fixture)
        3) run the upcoming bookings task and check that it finds the bookings created in #1 but does not
           find those created in #2
        4) run the booking notifications task on the bookings found in #3 (in a production environemnt this
           would be done automatically by the upcoming bookings task, but it must be explicitly called in
           testing)
        5) run the booking ehr task on the bookings found in #3 (same restriction as #4)
    """
    
    bookings = deploy_upcoming_appointment_tasks()

    assert len(bookings) == 3
        
    for booking in bookings:
        assert booking.notified == True
        upcoming_appointment_notification_2hr(booking.idx)        
        upcoming_appointment_care_team_permissions(booking.idx)
        
        care_team_permissions = test_client.db.session.execute(select(
            ClientClinicalCareTeamAuthorizations
        ).where(
            ClientClinicalCareTeamAuthorizations.user_id == booking.client_user_id, 
            ClientClinicalCareTeamAuthorizations.team_member_user_id == booking.staff_user_id
        )).scalars().all()

        resource_ids_needed = test_client.db.session.execute(select(
            LookupClinicalCareTeamResources.resource_id
        ).where(LookupClinicalCareTeamResources.access_group.in_(['general','medical_doctor', 'telehealth']))).scalars().all()

        assert len(care_team_permissions) == len(resource_ids_needed)
        
    notifications = test_client.db.session.execute(
    select(Notifications).
    where(
        Notifications.notification_type_id == 3,
        or_(
            Notifications.user_id == booking.client_user_id,
            Notifications.user_id == booking.staff_user_id))
    ).scalars().all()
    
    # in syntax is used to ensure the test can pass when run either on its own or in a suite
    # 2 notifications are created for each booking (one for cleint and one for practitioner) 
    # during this test and if the cancellation test has also been run an additional 1 
    # notification will exist 
    assert len(notifications) in [(len(bookings)*2), len(bookings)*2 + 1]