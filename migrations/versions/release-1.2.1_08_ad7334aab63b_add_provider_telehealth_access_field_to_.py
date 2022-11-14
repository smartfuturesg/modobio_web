"""Add provider_telehealth_access field to TelehealthSettings table

Revision ID: ad7334aab63b
Revises: 3669c98b6396
Create Date: 2022-11-02 10:07:32.995389

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ad7334aab63b'
down_revision = '3669c98b6396'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TelehealthStaffSettings', sa.Column('provider_telehealth_access', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TelehealthStaffSettings', 'provider_telehealth_access')
    # ### end Alembic commands ###
