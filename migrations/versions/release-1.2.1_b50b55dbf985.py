"""release-1.2.1

Added
- CommunityManagerSubscriptionGrants table
- ProviderCredentials table
- LookupCredentialTypes table
- User.is_provider added
- MedicalBloodTests.was_fasted 
- TelehealthBookings.email_reminded
- TelehealthStaffSettings.provider_telehealth_access
- LookupRoles.is_provider

Updated
- TelehealthBookings.payment_method_id made nullable
- TelehealthBookings.client_location_id made nullable
- TelehealthQueueClientPool.payment_method_id made nullable
- TelehealthQueueClientPool.location_id made nullable
- StaffRoles.consult_rate server defaulted to 0
- PractitionerCredentials.role_id made nullable

Removed
- PaymentStatus table
- DoseSpotPatientID table
- DoseSpotProxyID table
- DoseSpotPractitionerID table
- PaymentHistory.authorization_number 
- PaymentHistory.void_id 
- PaymentHistory.transaction_id 
- PaymentMethods.payment_id 
- PaymentRefunds.refund_transaction_id 
- MedicalBloodTests.panel_type 
- PractitionerCredentials.wants_to_practice

Revision ID: 0446b80e46cf
Revises: b9131229632d
Create Date: 2023-03-27 15:55:32.805014

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b50b55dbf985'
down_revision = 'b9131229632d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupEmotes',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('icon_name', sa.String(), nullable=True),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('title_text', sa.String(), nullable=True),
    sa.Column('content_text', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('idx'),
    sa.UniqueConstraint('position')
    )

    op.create_table('LookupCredentialTypes',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('credential_type', sa.String(), nullable=True),
    sa.Column('display_name', sa.String(), nullable=True),
    sa.Column('country_required', sa.Boolean(), nullable=True),
    sa.Column('sub_territory_required', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('idx'),
    sa.UniqueConstraint('credential_type')
    )
    op.create_table('CommunityManagerSubscriptionGrants',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('subscription_grantee_user_id', sa.Integer(), nullable=True),
    sa.Column('subscription_type_id', sa.Integer(), nullable=True),
    sa.Column('sponsor', sa.String(length=75), nullable=False),
    sa.Column('activated', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['subscription_grantee_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subscription_type_id'], ['LookupSubscriptions.sub_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', 'user_id'),
    sa.UniqueConstraint('idx')
    )
    op.create_table('ProviderRoleRequests',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('reviewer_user_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['reviewer_user_id'], ['User.user_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['role_id'], ['LookupRoles.idx'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('ProviderCredentials',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('country_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('credential_type', sa.String(), nullable=True),
    sa.Column('credentials', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('expiration_date', sa.Date(), nullable=True),
    sa.Column('role_request_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['LookupCountriesOfOperations.idx'], ),
    sa.ForeignKeyConstraint(['role_id'], ['StaffRoles.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_request_id'], ['ProviderRoleRequests.idx'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.drop_table('DoseSpotPatientID')
    op.drop_table('DoseSpotPractitionerID')
    op.drop_table('DoseSpotProxyID')
    op.drop_table('PaymentStatus')
    with op.batch_alter_table('LookupRoles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_provider', sa.Boolean(), nullable=True))

    with op.batch_alter_table('MedicalBloodTests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('was_fasted', sa.Boolean(), nullable=True))
        batch_op.drop_column('panel_type')

    with op.batch_alter_table('PaymentHistory', schema=None) as batch_op:
        batch_op.drop_column('void_id')
        batch_op.drop_column('transaction_id')
        batch_op.drop_column('authorization_number')

    with op.batch_alter_table('PaymentMethods', schema=None) as batch_op:
        batch_op.drop_column('payment_id')

    with op.batch_alter_table('PaymentRefunds', schema=None) as batch_op:
        batch_op.drop_column('refund_transaction_id')

    with op.batch_alter_table('PractitionerCredentials', schema=None) as batch_op:
        batch_op.alter_column('role_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.drop_column('want_to_practice')

    with op.batch_alter_table('TelehealthBookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_reminded', sa.Boolean(), nullable=True))
        batch_op.alter_column('client_location_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('TelehealthQueueClientPool', schema=None) as batch_op:
        batch_op.alter_column('location_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('TelehealthStaffSettings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('provider_telehealth_access', sa.Boolean(), nullable=True))

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_provider', sa.Boolean(), server_default='false', nullable=False))

    with op.batch_alter_table('UserSubscriptions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sponsorship_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('user_subscriptions_cm_subscription_grant_idx_fk_relationship', 'CommunityManagerSubscriptionGrants', ['sponsorship_id'], ['idx'])

    op.alter_column('StaffRoles', 'consult_rate',
               server_default='0')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LookupEmotes')
    
    with op.batch_alter_table('UserSubscriptions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('sponsorship_id')

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.drop_column('is_provider')

    with op.batch_alter_table('TelehealthStaffSettings', schema=None) as batch_op:
        batch_op.drop_column('provider_telehealth_access')

    with op.batch_alter_table('TelehealthQueueClientPool', schema=None) as batch_op:
        batch_op.alter_column('payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('location_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('TelehealthBookings', schema=None) as batch_op:
        batch_op.alter_column('payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('client_location_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('email_reminded')

    with op.batch_alter_table('PractitionerCredentials', schema=None) as batch_op:
        batch_op.add_column(sa.Column('want_to_practice', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.alter_column('role_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('PaymentRefunds', schema=None) as batch_op:
        batch_op.add_column(sa.Column('refund_transaction_id', sa.VARCHAR(), autoincrement=False, nullable=True))

    with op.batch_alter_table('PaymentMethods', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_id', sa.VARCHAR(), autoincrement=False, nullable=True))

    with op.batch_alter_table('PaymentHistory', schema=None) as batch_op:
        batch_op.add_column(sa.Column('authorization_number', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('transaction_id', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('void_id', sa.VARCHAR(), autoincrement=False, nullable=True))

    with op.batch_alter_table('MedicalBloodTests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('panel_type', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_column('was_fasted')

    with op.batch_alter_table('LookupRoles', schema=None) as batch_op:
        batch_op.drop_column('is_provider')

    op.create_table('PaymentStatus',
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('idx', sa.INTEGER(), server_default=sa.text('nextval(\'"PaymentStatus_idx_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('card_present_status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('current_transaction_status_code', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('original_transaction_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('original_transaction_status_code', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('payment_transaction_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('request_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('save_on_file_transaction_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('transaction_action', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], name='PaymentStatus_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='PaymentStatus_pkey')
    )
    op.create_table('DoseSpotProxyID',
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('idx', sa.INTEGER(), server_default=sa.text('nextval(\'"DoseSpotProxyID_idx_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('ds_proxy_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('idx', name='DoseSpotProxyID_pkey')
    )
    op.create_table('DoseSpotPractitionerID',
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('idx', sa.INTEGER(), server_default=sa.text('nextval(\'"DoseSpotPractitionerID_idx_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('ds_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ds_enrollment_status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], name='DoseSpotPractitionerID_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='DoseSpotPractitionerID_pkey'),
    sa.UniqueConstraint('user_id', name='dosespot_practitioner_id_user_id_unique')
    )
    op.create_table('DoseSpotPatientID',
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('clock_timestamp()'), autoincrement=False, nullable=True),
    sa.Column('idx', sa.INTEGER(), server_default=sa.text('nextval(\'"DoseSpotPatientID_idx_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('ds_user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], name='DoseSpotPatientID_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='DoseSpotPatientID_pkey'),
    sa.UniqueConstraint('user_id', name='dosespot_patient_id_user_id_unique')
    )
    op.drop_table('ProviderCredentials')
    op.drop_table('ProviderRoleRequests')
    op.drop_table('CommunityManagerSubscriptionGrants')
    op.drop_table('LookupCredentialTypes')
    # ### end Alembic commands ###
