"""empty message

Revision ID: b9131229632d
Revises: 6be0e73cb0cc
Create Date: 2022-08-23 20:35:55.627289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9131229632d'
down_revision = '89a011cf13b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupVisitReasons',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reason', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['LookupRoles.idx'], ),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TelehealthStaffAvailabilityExceptions',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('exception_date', sa.Date(), nullable=False),
    sa.Column('exception_booking_window_id_start_time', sa.Integer(), nullable=False),
    sa.Column('exception_booking_window_id_end_time', sa.Integer(), nullable=False),
    sa.Column('is_busy', sa.Boolean(), nullable=False),
    sa.Column('label', sa.String(length=100), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['exception_booking_window_id_end_time'], ['LookupBookingTimeIncrements.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['exception_booking_window_id_start_time'], ['LookupBookingTimeIncrements.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.drop_column('LookupNotifications', 'symbol_color')
    op.drop_column('LookupNotifications', 'background_color')
    op.add_column('MedicalBloodTests', sa.Column('image_path', sa.String(), nullable=True))
    op.add_column('Notifications', sa.Column('persona_type', sa.String(length=10), nullable=True))
    op.drop_column('Notifications', 'time_to_live')
    op.add_column('PaymentHistory', sa.Column('transaction_descriptor', sa.String(), nullable=True))
    op.add_column('PaymentHistory', sa.Column('authorization_number', sa.String(), nullable=True))
    op.drop_constraint('PaymentHistory_booking_id_fkey', 'PaymentHistory', type_='foreignkey')
    op.drop_column('PaymentHistory', 'booking_id')
    op.add_column('TelehealthBookingDetails', sa.Column('reason_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'TelehealthBookingDetails', 'LookupVisitReasons', ['reason_id'], ['idx'])
    op.add_column('TelehealthBookings', sa.Column('notified', sa.Boolean(), nullable=True))
    op.add_column('TelehealthBookings', sa.Column('payment_history_id', sa.Integer(), nullable=True))
    op.add_column('TelehealthBookings', sa.Column('scheduled_duration_mins', sa.Integer(), nullable=True))
    op.add_column('TelehealthBookings', sa.Column('payment_notified', sa.Boolean(), nullable=True))
    op.create_foreign_key(None, 'TelehealthBookings', 'PaymentHistory', ['payment_history_id'], ['idx'])
    op.add_column('UserLogin', sa.Column('staff_account_closed_reason', sa.String(length=500), nullable=True))
    op.add_column('UserLogin', sa.Column('client_account_closed_reason', sa.String(length=500), nullable=True))
    op.add_column('UserPendingEmailVerifications', sa.Column('email', sa.String(length=75), nullable=True))
    op.create_unique_constraint(None, 'UserPendingEmailVerifications', ['user_id'])
    op.create_unique_constraint(None, 'UserPendingEmailVerifications', ['email'])
    # ### manual additions     ###
    op.add_column('User', sa.Column('gender', sa.String(length=1), nullable=True))
    op.create_table('UserActiveCampaign',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('active_campaign_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('UserActiveCampaignTags',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('tag_name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'UserPendingEmailVerifications', type_='unique')
    op.drop_constraint(None, 'UserPendingEmailVerifications', type_='unique')
    op.drop_column('UserPendingEmailVerifications', 'email')
    op.drop_column('UserLogin', 'client_account_closed_reason')
    op.drop_column('UserLogin', 'staff_account_closed_reason')
    op.drop_constraint(None, 'TelehealthBookings', type_='foreignkey')
    op.drop_column('TelehealthBookings', 'payment_notified')
    op.drop_column('TelehealthBookings', 'scheduled_duration_mins')
    op.drop_column('TelehealthBookings', 'payment_history_id')
    op.drop_column('TelehealthBookings', 'notified')
    op.drop_constraint(None, 'TelehealthBookingDetails', type_='foreignkey')
    op.drop_column('TelehealthBookingDetails', 'reason_id')
    op.add_column('PaymentHistory', sa.Column('booking_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('PaymentHistory_booking_id_fkey', 'PaymentHistory', 'TelehealthBookings', ['booking_id'], ['idx'], ondelete='SET NULL')
    op.drop_column('PaymentHistory', 'authorization_number')
    op.drop_column('PaymentHistory', 'transaction_descriptor')
    op.add_column('Notifications', sa.Column('time_to_live', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('Notifications', 'persona_type')
    op.drop_column('MedicalBloodTests', 'image_path')
    op.add_column('LookupNotifications', sa.Column('background_color', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('LookupNotifications', sa.Column('symbol_color', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_table('TelehealthStaffAvailabilityExceptions')
    op.drop_table('LookupVisitReasons')
    # ### manual additions     ###
    op.drop_column('User', 'gender')
    op.drop_table('UserActiveCampaignTags')
    op.drop_table('UserActiveCampaign')
    # ### end Alembic commands ###
