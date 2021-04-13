"""added client staff bookings

Revision ID: d58f3a93ee88
Revises: 1cda89151944
Create Date: 2021-03-19 18:26:29.144246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd58f3a93ee88'
down_revision = '1cda89151944'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TelehealthBookings',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_user_id', sa.Integer(), nullable=False),
    sa.Column('staff_user_id', sa.Integer(), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=True),
    sa.Column('booking_window_id_start_time', sa.Integer(), nullable=False),
    sa.Column('booking_window_id_end_time', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['booking_window_id_end_time'], ['LookupBookingTimeIncrements.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['booking_window_id_start_time'], ['LookupBookingTimeIncrements.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['staff_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('TelehealthBookings')
    # ### end Alembic commands ###
