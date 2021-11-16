"""Change ClientPushNotifications to ClientNotificationSettings.

Revision ID: cc0d0aaeb7d3
Revises: edc81a136dc8
Create Date: 2021-11-15 09:40:40.764037

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cc0d0aaeb7d3'
# down_revision = 'edc81a136dc8'
# Temp until MR https://gitlab.atventurepartners.tech/zan/odyssey/-/merge_requests/572 is merged.
down_revision = 'aa9b5a000691'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('ClientPushNotifications', 'ClientNotificationSettings')

def downgrade():
    op.rename_table('ClientNotificationSettings', 'ClientPushNotifications')
