"""release_5
- Add Telehealth LookupBookingTimeIncrements
- Add TelehealthStaffAvailability
- Add LookupEmergencyNumbers
- Add TelehealthBookings
- Add TelehealthChatRooms
- Add TelehealthBookingDetails
- Change MedicalSurgeries.client_user_id to user_id
- Add LookupProfessionColors
- Add UserTokenHistory
- Add ClientDataStorage
- Add proper relationships to Wearables
- Add booking_id fkey to TelehealthMeetingRooms
- Add Notifications & NotificationsPushRegistration
- Drop UserNotifications


Revision ID: c4c5c968b777
Revises: 5a0ae7ad37d1
Create Date: 2021-02-21 22:25:06.384768

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c4c5c968b777'
down_revision = '5a0ae7ad37d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupBookingTimeIncrements',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TelehealthStaffAvailability',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('day_of_week', sa.String(), nullable=True),
    sa.Column('booking_window_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['booking_window_id'], ['LookupBookingTimeIncrements.idx'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('LookupEmergencyNumbers',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('continent', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('service', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('idx', 'code')
    )
    op.create_table('TelehealthBookings',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_user_id', sa.Integer(), nullable=False),
    sa.Column('staff_user_id', sa.Integer(), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=True),
    sa.Column('profession_type', sa.String(), nullable=True),
    sa.Column('booking_window_id_start_time', sa.Integer(), nullable=False),
    sa.Column('booking_window_id_end_time', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['booking_window_id_end_time'], ['LookupBookingTimeIncrements.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['booking_window_id_start_time'], ['LookupBookingTimeIncrements.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['staff_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TelehealthChatRooms',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('room_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('room_name', sa.String(), nullable=True),
    sa.Column('conversation_sid', sa.String(), nullable=True),
    sa.Column('room_status', sa.String(), nullable=True),
    sa.Column('client_user_id', sa.Integer(), nullable=False),
    sa.Column('staff_user_id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], ),
    sa.ForeignKeyConstraint(['staff_user_id'], ['User.user_id'], ),
    sa.ForeignKeyConstraint(['booking_id'], ['TelehealthBookings.idx'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('room_id')
    )
    op.create_table('TelehealthBookingDetails',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('details', sa.String(), nullable=True),
    sa.Column('media', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['booking_id'], ['TelehealthBookings.idx'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.add_column('MedicalSurgeries', sa.Column('user_id', sa.Integer(), nullable=False))
    op.drop_constraint('MedicalSurgeries_client_user_id_fkey', 'MedicalSurgeries', type_='foreignkey')
    op.create_foreign_key(None, 'MedicalSurgeries', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('MedicalSurgeries', 'client_user_id')
    op.create_table('LookupProfessionColors',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('profession_type', sa.String(), nullable=True),
    sa.Column('icon', sa.String(), nullable=True),
    sa.Column('color', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('UserTokenHistory',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('event', sa.String(), nullable=True),
    sa.Column('refresh_token', sa.String(), nullable=True),
    sa.Column('ua_string', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('ClientDataStorage',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('storage_tier', sa.String(), nullable=True),
    sa.Column('total_bytes', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.add_column('Wearables', sa.Column(
        'registered_freestyle',
        sa.Boolean(),
        server_default='f',
         nullable=True))
    op.alter_column('Wearables', 'registered_freestyle',
        existing_type=sa.BOOLEAN(),
        nullable=False)
    op.create_unique_constraint(None, 'Wearables', ['user_id'])
    op.add_column('WearablesFitbit', sa.Column('wearable_id', sa.Integer(), nullable=False))
    op.alter_column('WearablesFitbit', 'access_token',
               existing_type=sa.VARCHAR(length=512),
               type_=sa.String(length=1048),
               existing_nullable=True)
    op.create_unique_constraint(None, 'WearablesFitbit', ['wearable_id'])
    op.create_unique_constraint(None, 'WearablesFitbit', ['user_id'])
    op.create_foreign_key(None, 'WearablesFitbit', 'Wearables', ['wearable_id'], ['idx'], ondelete='CASCADE')
    op.add_column('WearablesFreeStyle', sa.Column('wearable_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'WearablesFreeStyle', ['user_id'])
    op.create_unique_constraint(None, 'WearablesFreeStyle', ['wearable_id'])
    op.create_foreign_key(None, 'WearablesFreeStyle', 'Wearables', ['wearable_id'], ['idx'], ondelete='CASCADE')
    op.add_column('WearablesOura', sa.Column('wearable_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'WearablesOura', ['user_id'])
    op.create_unique_constraint(None, 'WearablesOura', ['wearable_id'])
    op.create_foreign_key(None, 'WearablesOura', 'Wearables', ['wearable_id'], ['idx'], ondelete='CASCADE')
    op.add_column('TelehealthMeetingRooms', sa.Column('booking_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TelehealthMeetingRooms', 'TelehealthBookings', ['booking_id'], ['idx'], ondelete='CASCADE')
    op.create_table('Notifications',
    sa.Column('notification_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=True),
    sa.Column('content', sa.String(length=2048), nullable=True),
    sa.Column('action', sa.String(length=512), nullable=True),
    sa.Column('time_to_live', sa.Integer(), nullable=True),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.Column('read', sa.Boolean(), server_default='f', nullable=True),
    sa.Column('deleted', sa.Boolean(), server_default='f', nullable=True),
    sa.Column('notification_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['notification_type_id'], ['LookupNotifications.notification_type_id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('notification_id')
    )
    op.create_table('NotificationsPushRegistration',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('device_token', sa.String(length=1024), nullable=True),
    sa.Column('device_id', sa.String(length=1024), nullable=True),
    sa.Column('device_description', sa.String(length=1024), nullable=True),
    sa.Column('arn', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.drop_table('UserNotifications')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserNotifications',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('idx', sa.INTEGER(), server_default=sa.text('nextval(\'"UserNotifications_idx_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('notification_type_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('action', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('time_to_live', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_staff', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('read', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['notification_type_id'], ['LookupNotifications.notification_type_id'], name='UserNotifications_notification_type_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], name='UserNotifications_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='UserNotifications_pkey')
    )
    op.drop_table('NotificationsPushRegistration')
    op.drop_table('Notifications')
    op.drop_constraint(None, 'TelehealthMeetingRooms', type_='foreignkey')
    op.drop_column('TelehealthMeetingRooms', 'booking_id')
    op.drop_constraint("WearablesOura_wearable_id_fkey", 'WearablesOura', type_='foreignkey')
    op.drop_constraint("WearablesOura_wearable_id_key", 'WearablesOura', type_='unique')
    op.drop_constraint("WearablesOura_user_id_key", 'WearablesOura', type_='unique')
    op.drop_column('WearablesOura', 'wearable_id')
    op.drop_constraint("WearablesFreeStyle_wearable_id_fkey", 'WearablesFreeStyle', type_='foreignkey')
    op.drop_constraint("WearablesFreeStyle_wearable_id_key", 'WearablesFreeStyle', type_='unique')
    op.drop_constraint("WearablesFreeStyle_user_id_key", 'WearablesFreeStyle', type_='unique')
    op.drop_column('WearablesFreeStyle', 'wearable_id')
    op.drop_constraint("WearablesFitbit_wearable_id_fkey", 'WearablesFitbit', type_='foreignkey')
    op.drop_constraint("WearablesFitbit_wearable_id_key", 'WearablesFitbit', type_='unique')
    op.drop_constraint("WearablesFitbit_user_id_key", 'WearablesFitbit', type_='unique')
    op.alter_column('WearablesFitbit', 'access_token',
               existing_type=sa.String(length=1048),
               type_=sa.VARCHAR(length=512),
               existing_nullable=True)
    op.drop_column('WearablesFitbit', 'wearable_id')
    op.drop_constraint("Wearables_user_id_key", 'Wearables', type_='unique')
    op.drop_column('Wearables', 'registered_freestyle')
    op.drop_table('ClientDataStorage')
    op.drop_table('UserTokenHistory')
    op.drop_table('LookupProfessionColors')
    op.add_column('MedicalSurgeries', sa.Column('client_user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'MedicalSurgeries', type_='foreignkey')
    op.create_foreign_key('MedicalSurgeries_client_user_id_fkey', 'MedicalSurgeries', 'User', ['client_user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('MedicalSurgeries', 'user_id')
    op.drop_table('TelehealthBookingDetails')
    op.drop_table('TelehealthChatRooms')
    op.drop_table('TelehealthBookings')
    op.drop_table('LookupEmergencyNumbers')
    op.drop_table('TelehealthStaffAvailability')
    op.drop_table('LookupBookingTimeIncrements')
    # ### end Alembic commands ###
