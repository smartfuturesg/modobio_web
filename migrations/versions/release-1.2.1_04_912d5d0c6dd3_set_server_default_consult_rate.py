"""Set the server default consult_rate to 0

Revision ID: 912d5d0c6dd3
Revises: 09bd96cf3eb5
Create Date: 2022-10-20 17:47:08.523894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '912d5d0c6dd3'
down_revision = '09bd96cf3eb5'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('StaffRoles', 'consult_rate',
               server_default='0')


def downgrade():
    op.alter_column('StaffRoles', 'consult_rate',
               server_default=None)
