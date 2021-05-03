
from celery.schedules import crontab
from sqlalchemy import delete, text

from odyssey import celery, db
from odyssey.api.client.models import ClientDataStorage


@celery.task()
def refresh_client_data_storage():
    """
    Use data_per_client view to update ClientDataStorage table
    """
    dat = db.session.execute(
        text("SELECT * FROM public.data_per_client")
    ).all()
    db.session.execute(delete(ClientDataStorage))
    db.session.flush()

    for row in dat:
        db.session.add(ClientDataStorage(user_id=row[0], total_bytes=row[1], storage_tier=row[2]))
    db.session.commit()

    return

celery.conf.beat_schedule = {
    # refresh the client data storage table every day at midnight
    'add-update-client-data-storage-table': {
        'task': 'odyssey.tasks.periodic.refresh_client_data_storage',
        'schedule': crontab(hour=0, minute=0)
    },
}
