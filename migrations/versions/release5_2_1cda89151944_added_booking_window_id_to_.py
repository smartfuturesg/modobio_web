"""added booking_window_id to staffavailability table

Revision ID: 1cda89151944
Revises: 342bfe80cc99
Create Date: 2021-03-12 15:12:29.623517

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1cda89151944'
down_revision = '0a355c29b670'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TelehealthStaffAvailability', sa.Column('booking_window_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TelehealthStaffAvailability', 'LookupBookingTimeIncrements', ['booking_window_id'], ['idx'], ondelete='CASCADE')
    op.drop_column('TelehealthStaffAvailability', 'end_time')
    op.drop_column('TelehealthStaffAvailability', 'start_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TelehealthStaffAvailability', sa.Column('start_time', postgresql.TIME(), autoincrement=False, nullable=True))
    op.add_column('TelehealthStaffAvailability', sa.Column('end_time', postgresql.TIME(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'TelehealthStaffAvailability', type_='foreignkey')
    op.drop_column('TelehealthStaffAvailability', 'booking_window_id')
    # ### end Alembic commands ###
