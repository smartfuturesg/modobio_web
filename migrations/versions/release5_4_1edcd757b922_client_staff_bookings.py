"""client staff bookings

Revision ID: 1edcd757b922
Revises: 342bfe80cc99
Create Date: 2021-03-14 17:11:29.312490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1edcd757b922'
down_revision = '0a355c29b670'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TelehealthClientStaffBookings',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_user_id', sa.Integer(), nullable=False),
    sa.Column('staff_user_id', sa.Integer(), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=True),
    sa.Column('booking_window_id_start_time', sa.Integer(), nullable=True),
    sa.Column('booking_window_id_end_time', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['staff_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('TelehealthClientStaffBookings')
    # ### end Alembic commands ###
