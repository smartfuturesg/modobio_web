"""Change ClientPushNotifications to ClientNotificationSettings.

Revision ID: cc0d0aaeb7d3
Revises: 9742ee54316f
Create Date: 2021-11-15 09:40:40.764037

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cc0d0aaeb7d3'
down_revision = '9742ee54316f'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('ClientPushNotifications', 'ClientNotificationSettings')

def downgrade():
    op.rename_table('ClientNotificationSettings', 'ClientPushNotifications')
