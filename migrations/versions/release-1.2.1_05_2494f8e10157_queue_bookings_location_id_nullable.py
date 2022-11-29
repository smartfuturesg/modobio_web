"""Make location_id nullable for TelehealthQueueClientPool and TelehealthBookings

Revision ID: 2494f8e10157
Revises: 912d5d0c6dd3
Create Date: 2022-10-18 12:37:54.134866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2494f8e10157'
down_revision = '912d5d0c6dd3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('TelehealthQueueClientPool', 'location_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('TelehealthBookings', 'client_location_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('TelehealthQueueClientPool', 'location_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('TelehealthBookings', 'client_location_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    ### end Alembic commands ###
