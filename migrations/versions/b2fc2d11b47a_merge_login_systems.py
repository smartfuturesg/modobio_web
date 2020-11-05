"""Merge login systems

Revision ID: b2fc2d11b47a
Revises: 181802f48ef7
Create Date: 2020-10-23 15:59:29.122796

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2fc2d11b47a'
down_revision = '0ca6be8dfbb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('modobio_id', sa.String(), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('phone_number', sa.String(length=50), nullable=True),
    sa.Column('firstname', sa.String(length=50), nullable=True),
    sa.Column('middlename', sa.String(length=50), nullable=True),
    sa.Column('lastname', sa.String(length=50), nullable=True),
    sa.Column('is_staff', sa.Boolean(), nullable=False),
    sa.Column('is_client', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('StaffProfile',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('membersince', sa.DateTime(), nullable=True),
    sa.Column('bio', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('UserLogin',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('password_created_at', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_index(op.f('ix_UserLogin_token'), 'UserLogin', ['token'], unique=True)
    op.drop_constraint('ClientConsent_clientid_fkey', 'ClientConsent', type_='foreignkey')    
    op.drop_constraint('ClientColusultContract_clientid_fkey', 'ClientConsultContract', type_='foreignkey')    
    op.drop_constraint('ClientExternalMR_clientid_med_record_id_institute_id_key', 'ClientExternalMR', type_='unique')    
    op.drop_constraint('ClientExternalMR_clientid_fkey', 'ClientExternalMR', type_='foreignkey')    
    op.drop_constraint('ClientFacilities_client_id_fkey', 'ClientFacilities', type_='foreignkey')    
    op.drop_constraint('ClientIndividualContract_clientid_fkey', 'ClientIndividualContract', type_='foreignkey')    
    op.drop_constraint('ClientPolicies_clientid_fkey', 'ClientPolicies', type_='foreignkey')    
    op.drop_constraint('ClientRelease_clientid_fkey', 'ClientRelease', type_='foreignkey')    
    op.drop_constraint('ClientReleaseContacts_clientid_fkey', 'ClientReleaseContacts', type_='foreignkey')    
    op.drop_constraint('ClientRemovalRequests_staffid_fkey', 'ClientRemovalRequests', type_='foreignkey')
    op.drop_constraint('ClientSubscriptionContract_clientid_fkey', 'ClientSubscriptionContract', type_='foreignkey')    
    op.drop_constraint('MedicalBloodTestResults_testid_fkey', 'MedicalBloodTestResults', type_='foreignkey')
    op.drop_constraint('MedicalBloodTests_clientid_fkey', 'MedicalBloodTests', type_='foreignkey')    
    op.drop_constraint('MedicalBloodTestResults_resultid_fkey', 'MedicalBloodTestResults', type_='foreignkey')    
    op.drop_constraint('MedicalHistory_clientid_fkey', 'MedicalHistory', type_='foreignkey')    
    op.drop_constraint('MedicalImaging_clientid_fkey', 'MedicalImaging', type_='foreignkey')    
    op.drop_constraint('MedicalPhysicalExam_clientid_fkey', 'MedicalPhysicalExam', type_='foreignkey')    
    op.drop_constraint('MobilityAssessment_clientid_fkey', 'MobilityAssessment', type_='foreignkey')    
    op.drop_constraint('chessboard_clientid_fkey', 'PTChessboard', type_='foreignkey')    
    op.drop_constraint('PTHistory_clientid_fkey', 'PTHistory', type_='foreignkey')    
    op.drop_constraint('fitness_questionnaire_clientid_fkey', 'TrainerFitnessQuestionnaire', type_='foreignkey')
    op.drop_constraint('heart_assessment_clientid_fkey', 'TrainerHeartAssessment', type_='foreignkey')    
    op.drop_constraint('lung_assessment_clientid_fkey', 'TrainerLungAssessment', type_='foreignkey')    
    op.drop_constraint('movement_assessment_clientid_fkey', 'TrainerMovementAssessment', type_='foreignkey')    
    op.drop_constraint('moxy_assessment_clientid_fkey', 'TrainerMoxyAssessment', type_='foreignkey')    
    op.drop_constraint('moxy_rip_assessment_clientid_fkey', 'TrainerMoxyRipTest', type_='foreignkey')
    op.drop_constraint('power_assessment_clientid_fkey', 'TrainerPowerAssessment', type_='foreignkey')    
    op.drop_constraint('strength_assessment_clientid_fkey', 'TrainerStrengthAssessment', type_='foreignkey')    
    op.drop_constraint('Wearables_clientid_fkey', 'Wearables', type_='foreignkey')    
    op.drop_constraint('WearablesFreeStyle_clientid_fkey', 'WearablesFreeStyle', type_='foreignkey')    
    op.drop_constraint('WearablesOura_clientid_fkey', 'WearablesOura', type_='foreignkey')    
    op.drop_index('ix_ClientRemoteRegistration_registration_portal_id', table_name='ClientRemoteRegistration')
    op.drop_index('ix_ClientRemoteRegistration_token', table_name='ClientRemoteRegistration')
    op.drop_table('ClientRemoteRegistration')
    op.drop_table('ClientInfo')
    op.create_table('ClientInfo',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('membersince', sa.DateTime(), nullable=True),
    sa.Column('guardianname', sa.String(length=100), nullable=True),
    sa.Column('guardianrole', sa.String(length=50), nullable=True),
    sa.Column('street', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=50), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('zipcode', sa.String(length=10), nullable=True),
    sa.Column('country', sa.String(length=2), nullable=True),
    sa.Column('preferred', sa.SmallInteger(), nullable=True),
    sa.Column('emergency_contact', sa.String(length=50), nullable=True),
    sa.Column('emergency_phone', sa.String(length=20), nullable=True),
    sa.Column('healthcare_contact', sa.String(length=50), nullable=True),
    sa.Column('healthcare_phone', sa.String(length=20), nullable=True),
    sa.Column('gender', sa.String(length=1), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('profession', sa.String(length=100), nullable=True),
    sa.Column('receive_docs', sa.Boolean(), nullable=True),
    sa.Column('record_locator_id', sa.String(length=12), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.drop_index('ix_Staff_token', table_name='Staff')
    op.add_column('ClientConsent', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientConsent', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientConsent', 'clientid')
    op.add_column('ClientConsultContract', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientConsultContract', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientConsultContract', 'clientid')
    op.add_column('ClientExternalMR', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'ClientExternalMR', ['user_id', 'med_record_id', 'institute_id'])
    op.create_foreign_key(None, 'ClientExternalMR', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientExternalMR', 'clientid')
    op.add_column('ClientFacilities', sa.Column('user_id', sa.Integer(), nullable=False))
    op.alter_column('ClientFacilities', 'facility_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key(None, 'ClientFacilities', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientFacilities', 'client_id')
    op.add_column('ClientIndividualContract', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientIndividualContract', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientIndividualContract', 'clientid')
    op.add_column('ClientPolicies', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientPolicies', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientPolicies', 'clientid')
    op.add_column('ClientRelease', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientRelease', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientRelease', 'clientid')
    op.add_column('ClientReleaseContacts', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientReleaseContacts', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientReleaseContacts', 'clientid')
    op.add_column('ClientRemovalRequests', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientRemovalRequests', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientRemovalRequests', 'staffid')
    op.add_column('ClientSubscriptionContract', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ClientSubscriptionContract', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('ClientSubscriptionContract', 'clientid')
    op.alter_column('MedicalBloodTests', 'testid', nullable=False, new_column_name='test_id')
    op.add_column('MedicalBloodTests', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'MedicalBloodTests', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('MedicalBloodTests', 'clientid')
    op.alter_column('MedicalBloodTestResultTypes', 'resultid', nullable=False, new_column_name='result_id')
    op.add_column('MedicalBloodTestResults', sa.Column('result_id', sa.Integer(), nullable=False))
    op.add_column('MedicalBloodTestResults', sa.Column('test_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'MedicalBloodTestResults', 'MedicalBloodTestResultTypes', ['result_id'], ['result_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'MedicalBloodTestResults', 'MedicalBloodTests', ['test_id'], ['test_id'], ondelete='CASCADE')
    op.drop_column('MedicalBloodTestResults', 'testid')
    op.drop_column('MedicalBloodTestResults', 'resultid')
    op.add_column('MedicalHistory', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'MedicalHistory', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('MedicalHistory', 'clientid')
    op.add_column('MedicalImaging', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'MedicalImaging', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('MedicalImaging', 'clientid')
    op.add_column('MedicalPhysicalExam', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'MedicalPhysicalExam', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('MedicalPhysicalExam', 'clientid')
    op.add_column('MobilityAssessment', sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('MobilityAssessment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'MobilityAssessment', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('MobilityAssessment', 'clientid')
    op.add_column('PTChessboard', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'PTChessboard', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('PTChessboard', 'clientid')
    op.add_column('PTHistory', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'PTHistory', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('PTHistory', 'clientid')
    op.add_column('TrainerFitnessQuestionnaire', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerFitnessQuestionnaire', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerFitnessQuestionnaire', 'clientid')
    op.add_column('TrainerHeartAssessment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerHeartAssessment', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerHeartAssessment', 'clientid')
    op.add_column('TrainerLungAssessment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerLungAssessment', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerLungAssessment', 'clientid')
    op.add_column('TrainerMovementAssessment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerMovementAssessment', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerMovementAssessment', 'clientid')
    op.add_column('TrainerMoxyAssessment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerMoxyAssessment', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerMoxyAssessment', 'clientid')
    op.add_column('TrainerMoxyRipTest', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerMoxyRipTest', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerMoxyRipTest', 'clientid')
    op.add_column('TrainerPowerAssessment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerPowerAssessment', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerPowerAssessment', 'clientid')
    op.add_column('TrainerStrengthAssessment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TrainerStrengthAssessment', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('TrainerStrengthAssessment', 'clientid')
    op.add_column('Wearables', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'Wearables', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('Wearables', 'clientid')
    op.add_column('WearablesFreeStyle', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'WearablesFreeStyle', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('WearablesFreeStyle', 'clientid')
    op.add_column('WearablesOura', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'WearablesOura', 'User', ['user_id'], ['user_id'], ondelete='CASCADE')
    op.drop_column('WearablesOura', 'clientid')
    op.drop_table('Staff')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('WearablesOura', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'WearablesOura', type_='foreignkey')
    op.create_foreign_key('WearablesOura_clientid_fkey', 'WearablesOura', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('WearablesOura', 'user_id')
    op.add_column('WearablesFreeStyle', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'WearablesFreeStyle', type_='foreignkey')
    op.create_foreign_key('WearablesFreeStyle_clientid_fkey', 'WearablesFreeStyle', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('WearablesFreeStyle', 'user_id')
    op.add_column('Wearables', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'Wearables', type_='foreignkey')
    op.create_foreign_key('Wearables_clientid_fkey', 'Wearables', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('Wearables', 'user_id')
    op.add_column('TrainerStrengthAssessment', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerStrengthAssessment', type_='foreignkey')
    op.create_foreign_key('strength_assessment_clientid_fkey', 'TrainerStrengthAssessment', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerStrengthAssessment', 'user_id')
    op.add_column('TrainerPowerAssessment', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerPowerAssessment', type_='foreignkey')
    op.create_foreign_key('power_assessment_clientid_fkey', 'TrainerPowerAssessment', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerPowerAssessment', 'user_id')
    op.add_column('TrainerMoxyRipTest', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerMoxyRipTest', type_='foreignkey')
    op.create_foreign_key('moxy_rip_assessment_clientid_fkey', 'TrainerMoxyRipTest', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerMoxyRipTest', 'user_id')
    op.add_column('TrainerMoxyAssessment', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerMoxyAssessment', type_='foreignkey')
    op.create_foreign_key('moxy_assessment_clientid_fkey', 'TrainerMoxyAssessment', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerMoxyAssessment', 'user_id')
    op.add_column('TrainerMovementAssessment', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerMovementAssessment', type_='foreignkey')
    op.create_foreign_key('movement_assessment_clientid_fkey', 'TrainerMovementAssessment', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerMovementAssessment', 'user_id')
    op.add_column('TrainerLungAssessment', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerLungAssessment', type_='foreignkey')
    op.create_foreign_key('lung_assessment_clientid_fkey', 'TrainerLungAssessment', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerLungAssessment', 'user_id')
    op.add_column('TrainerHeartAssessment', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerHeartAssessment', type_='foreignkey')
    op.create_foreign_key('heart_assessment_clientid_fkey', 'TrainerHeartAssessment', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerHeartAssessment', 'user_id')
    op.add_column('TrainerFitnessQuestionnaire', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'TrainerFitnessQuestionnaire', type_='foreignkey')
    op.create_foreign_key('fitness_questionnaire_clientid_fkey', 'TrainerFitnessQuestionnaire', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('TrainerFitnessQuestionnaire', 'user_id')
    op.add_column('PTHistory', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'PTHistory', type_='foreignkey')
    op.create_foreign_key('PTHistory_clientid_fkey', 'PTHistory', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('PTHistory', 'user_id')
    op.add_column('PTChessboard', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'PTChessboard', type_='foreignkey')
    op.create_foreign_key('chessboard_clientid_fkey', 'PTChessboard', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('PTChessboard', 'user_id')
    op.add_column('MobilityAssessment', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'MobilityAssessment', type_='foreignkey')
    op.create_foreign_key('MobilityAssessment_clientid_fkey', 'MobilityAssessment', 'ClientInfo', ['clientid'], ['clientid'])
    op.alter_column('MobilityAssessment', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('MobilityAssessment', 'user_id')
    op.drop_column('MobilityAssessment', 'idx')
    op.add_column('MedicalPhysicalExam', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'MedicalPhysicalExam', type_='foreignkey')
    op.create_foreign_key('MedicalPhysicalExam_clientid_fkey', 'MedicalPhysicalExam', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('MedicalPhysicalExam', 'user_id')
    op.add_column('MedicalImaging', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'MedicalImaging', type_='foreignkey')
    op.create_foreign_key('MedicalImaging_clientid_fkey', 'MedicalImaging', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('MedicalImaging', 'user_id')
    op.add_column('MedicalHistory', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'MedicalHistory', type_='foreignkey')
    op.create_foreign_key('MedicalHistory_clientid_fkey', 'MedicalHistory', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('MedicalHistory', 'user_id')
    op.add_column('MedicalBloodTests', sa.Column('testid', sa.INTEGER(), server_default=sa.text('nextval(\'"MedicalBloodTests_testid_seq"\'::regclass)'), autoincrement=True, nullable=False))
    op.add_column('MedicalBloodTests', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'MedicalBloodTests', type_='foreignkey')
    op.create_foreign_key('MedicalBloodTests_clientid_fkey', 'MedicalBloodTests', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('MedicalBloodTests', 'user_id')
    op.drop_column('MedicalBloodTests', 'test_id')
    op.add_column('MedicalBloodTestResults', sa.Column('resultid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('MedicalBloodTestResults', sa.Column('testid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'MedicalBloodTestResults', type_='foreignkey')
    op.drop_constraint(None, 'MedicalBloodTestResults', type_='foreignkey')
    op.create_foreign_key('MedicalBloodTestResults_resultid_fkey', 'MedicalBloodTestResults', 'MedicalBloodTestResultTypes', ['resultid'], ['resultid'], ondelete='CASCADE')
    op.create_foreign_key('MedicalBloodTestResults_testid_fkey', 'MedicalBloodTestResults', 'MedicalBloodTests', ['testid'], ['testid'], ondelete='CASCADE')
    op.drop_column('MedicalBloodTestResults', 'test_id')
    op.drop_column('MedicalBloodTestResults', 'result_id')
    op.add_column('MedicalBloodTestResultTypes', sa.Column('resultid', sa.INTEGER(), server_default=sa.text('nextval(\'"MedicalBloodTestResultTypes_resultid_seq"\'::regclass)'), autoincrement=True, nullable=False))
    op.drop_column('MedicalBloodTestResultTypes', 'result_id')
    op.add_column('ClientSubscriptionContract', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientSubscriptionContract', type_='foreignkey')
    op.create_foreign_key('ClientSubscriptionContract_clientid_fkey', 'ClientSubscriptionContract', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('ClientSubscriptionContract', 'user_id')
    op.add_column('ClientRemovalRequests', sa.Column('staffid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientRemovalRequests', type_='foreignkey')
    op.create_foreign_key('ClientRemovalRequests_staffid_fkey', 'ClientRemovalRequests', 'Staff', ['staffid'], ['staffid'])
    op.drop_column('ClientRemovalRequests', 'user_id')
    op.add_column('ClientReleaseContacts', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientReleaseContacts', type_='foreignkey')
    op.create_foreign_key('ClientReleaseContacts_clientid_fkey', 'ClientReleaseContacts', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('ClientReleaseContacts', 'user_id')
    op.add_column('ClientRelease', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientRelease', type_='foreignkey')
    op.create_foreign_key('ClientRelease_clientid_fkey', 'ClientRelease', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('ClientRelease', 'user_id')
    op.add_column('ClientPolicies', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientPolicies', type_='foreignkey')
    op.create_foreign_key('ClientPolicies_clientid_fkey', 'ClientPolicies', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('ClientPolicies', 'user_id')
    op.add_column('ClientInfo', sa.Column('fullname', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('middlename', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('ringsize', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('clientid', sa.INTEGER(), server_default=sa.text('nextval(\'"ClientInfo_clientid_seq"\'::regclass)'), autoincrement=True, nullable=False))
    op.add_column('ClientInfo', sa.Column('phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('lastname', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('firstname', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('address', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'ClientInfo', type_='foreignkey')
    op.drop_column('ClientInfo', 'user_id')
    op.drop_column('ClientInfo', 'idx')
    op.drop_column('ClientInfo', 'created_at')
    op.add_column('ClientIndividualContract', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientIndividualContract', type_='foreignkey')
    op.create_foreign_key('ClientIndividualContract_clientid_fkey', 'ClientIndividualContract', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('ClientIndividualContract', 'user_id')
    op.add_column('ClientFacilities', sa.Column('client_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'ClientFacilities', type_='foreignkey')
    op.create_foreign_key('ClientFacilities_client_id_fkey', 'ClientFacilities', 'ClientInfo', ['client_id'], ['clientid'], ondelete='CASCADE')
    op.alter_column('ClientFacilities', 'facility_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('ClientFacilities', 'user_id')
    op.add_column('ClientExternalMR', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientExternalMR', type_='foreignkey')
    op.create_foreign_key('ClientExternalMR_clientid_fkey', 'ClientExternalMR', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_constraint(None, 'ClientExternalMR', type_='unique')
    op.create_unique_constraint('ClientExternalMR_clientid_med_record_id_institute_id_key', 'ClientExternalMR', ['clientid', 'med_record_id', 'institute_id'])
    op.drop_column('ClientExternalMR', 'user_id')
    op.add_column('ClientConsultContract', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientConsultContract', type_='foreignkey')
    op.create_foreign_key('ClientColusultContract_clientid_fkey', 'ClientConsultContract', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('ClientConsultContract', 'user_id')
    op.add_column('ClientConsent', sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ClientConsent', type_='foreignkey')
    op.create_foreign_key('ClientConsent_clientid_fkey', 'ClientConsent', 'ClientInfo', ['clientid'], ['clientid'], ondelete='CASCADE')
    op.drop_column('ClientConsent', 'user_id')
    op.create_table('Staff',
    sa.Column('staffid', sa.INTEGER(), server_default=sa.text('nextval(\'"Staff_staffid_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('firstname', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('lastname', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('fullname', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('password', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('token', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('token_expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_system_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('access_roles', postgresql.ARRAY(sa.VARCHAR()), server_default=sa.text("'{}'::character varying[]"), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('staffid', name='Staff_pkey'),
    sa.UniqueConstraint('email', name='Staff_email_key')
    )
    op.create_index('ix_Staff_token', 'Staff', ['token'], unique=True)
    op.create_table('ClientRemoteRegistration',
    sa.Column('idx', sa.INTEGER(), server_default=sa.text('nextval(\'"ClientRemoteRegistration_idx_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('token', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('token_expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('password', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('registration_portal_id', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('registration_portal_expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='remote_registration_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='ClientRemoteRegistration_pkey')
    )
    op.create_index('ix_ClientRemoteRegistration_token', 'ClientRemoteRegistration', ['token'], unique=True)
    op.create_index('ix_ClientRemoteRegistration_registration_portal_id', 'ClientRemoteRegistration', ['registration_portal_id'], unique=True)
    op.drop_index(op.f('ix_UserLogin_token'), table_name='UserLogin')
    op.drop_table('UserLogin')
    op.drop_table('StaffProfile')
    op.drop_table('User')
    # ### end Alembic commands ###
