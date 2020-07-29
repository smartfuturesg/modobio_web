"""normalize table names to CaMeLCaSe

Revision ID: bdc2108da9b8
Revises: 3456e4ca6c0f
Create Date: 2020-07-29 12:11:55.992670

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bdc2108da9b8'
down_revision = '3456e4ca6c0f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ClientRemoteRegistration',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('registration_portal_id', sa.String(length=32), nullable=True),
    sa.Column('registration_portal_expiration', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='remote_registration_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_index(op.f('ix_ClientRemoteRegistration_registration_portal_id'), 'ClientRemoteRegistration', ['registration_portal_id'], unique=True)
    op.create_index(op.f('ix_ClientRemoteRegistration_token'), 'ClientRemoteRegistration', ['token'], unique=True)
    op.create_table('ClientRemovalRequests',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('staffid', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['staffid'], ['Staff.staffid'], name='ClientRemovalRequests_staffid_fkey'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('PTChessboard',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('isa_right', sa.Boolean(), nullable=True),
    sa.Column('isa_left', sa.Boolean(), nullable=True),
    sa.Column('isa_structure', sa.String(length=24), nullable=True),
    sa.Column('isa_dynamic', sa.Boolean(), nullable=True),
    sa.Column('left_shoulder_er', sa.Integer(), nullable=True),
    sa.Column('left_shoulder_ir', sa.Integer(), nullable=True),
    sa.Column('left_shoulder_abd', sa.Integer(), nullable=True),
    sa.Column('left_shoulder_add', sa.Integer(), nullable=True),
    sa.Column('left_shoulder_flexion', sa.Integer(), nullable=True),
    sa.Column('left_shoulder_extension', sa.Integer(), nullable=True),
    sa.Column('right_shoulder_er', sa.Integer(), nullable=True),
    sa.Column('right_shoulder_ir', sa.Integer(), nullable=True),
    sa.Column('right_shoulder_abd', sa.Integer(), nullable=True),
    sa.Column('right_shoulder_add', sa.Integer(), nullable=True),
    sa.Column('right_shoulder_flexion', sa.Integer(), nullable=True),
    sa.Column('right_shoulder_extension', sa.Integer(), nullable=True),
    sa.Column('left_hip_slr', sa.Integer(), nullable=True),
    sa.Column('left_hip_er', sa.Integer(), nullable=True),
    sa.Column('left_hip_ir', sa.Integer(), nullable=True),
    sa.Column('left_hip_abd', sa.Integer(), nullable=True),
    sa.Column('left_hip_add', sa.Integer(), nullable=True),
    sa.Column('left_hip_flexion', sa.Integer(), nullable=True),
    sa.Column('left_hip_extension', sa.Integer(), nullable=True),
    sa.Column('right_hip_er', sa.Integer(), nullable=True),
    sa.Column('right_hip_ir', sa.Integer(), nullable=True),
    sa.Column('right_hip_abd', sa.Integer(), nullable=True),
    sa.Column('right_hip_add', sa.Integer(), nullable=True),
    sa.Column('right_hip_flexion', sa.Integer(), nullable=True),
    sa.Column('right_hip_extension', sa.Integer(), nullable=True),
    sa.Column('right_hip_slr', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='chessboard_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TrainerHeartAssessment',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('resting_hr', sa.Integer(), nullable=True),
    sa.Column('max_hr', sa.Integer(), nullable=True),
    sa.Column('theoretical_max_hr', sa.Integer(), nullable=True),
    sa.Column('avg_eval_hr', sa.Integer(), nullable=True),
    sa.Column('avg_training_hr', sa.Integer(), nullable=True),
    sa.Column('estimated_vo2_max', sa.Integer(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='heart_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TrainerLungAssessment',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('bag_size', sa.Float(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('breaths_per_minute', sa.Integer(), nullable=True),
    sa.Column('max_minute_volume', sa.Float(), nullable=True),
    sa.Column('liters_min_kg', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='lung_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TrainerMovementAssessment',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('squat_dept', sa.String(), nullable=True),
    sa.Column('squat_ramp', sa.String(), nullable=True),
    sa.Column('squat_eye_test', sa.Boolean(), nullable=True),
    sa.Column('squat_can_breathe', sa.Boolean(), nullable=True),
    sa.Column('squat_can_look_up', sa.Boolean(), nullable=True),
    sa.Column('toe_touch_depth', sa.String(), nullable=True),
    sa.Column('toe_touch_pelvis_movement', sa.String(), nullable=True),
    sa.Column('toe_touch_ribcage_movement', sa.String(), nullable=True),
    sa.Column('toe_touch_notes', sa.String(), nullable=True),
    sa.Column('standing_rotation_r_notes', sa.String(), nullable=True),
    sa.Column('standing_rotation_l_notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='movement_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TrainerMoxyAssessment',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('recovery_baseline', sa.Integer(), nullable=True),
    sa.Column('performance_baseline', sa.Integer(), nullable=True),
    sa.Column('gas_tank_size', sa.Integer(), nullable=True),
    sa.Column('starting_sm_o2', sa.Integer(), nullable=True),
    sa.Column('starting_thb', sa.Integer(), nullable=True),
    sa.Column('limiter', sa.String(), nullable=True),
    sa.Column('intervention', sa.String(), nullable=True),
    sa.Column('performance_metric_1', sa.String(), nullable=True),
    sa.Column('performance_metric_1_value', sa.Integer(), nullable=True),
    sa.Column('performance_metric_2', sa.String(), nullable=True),
    sa.Column('performance_metric_2_value', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='moxy_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TrainerMoxyRipTest',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('performance_smo2_1', sa.Integer(), nullable=True),
    sa.Column('performance_thb_1', sa.Integer(), nullable=True),
    sa.Column('performance_average_power_1', sa.Integer(), nullable=True),
    sa.Column('performance_hr_max_1', sa.Integer(), nullable=True),
    sa.Column('performance_smo2_2', sa.Integer(), nullable=True),
    sa.Column('performance_thb_2', sa.Integer(), nullable=True),
    sa.Column('performance_average_power_2', sa.Integer(), nullable=True),
    sa.Column('performance_hr_max_2', sa.Integer(), nullable=True),
    sa.Column('performance_smo2_3', sa.Integer(), nullable=True),
    sa.Column('performance_thb_3', sa.Integer(), nullable=True),
    sa.Column('performance_average_power_3', sa.Integer(), nullable=True),
    sa.Column('performance_hr_max_3', sa.Integer(), nullable=True),
    sa.Column('performance_smo2_4', sa.Integer(), nullable=True),
    sa.Column('performance_thb_4', sa.Integer(), nullable=True),
    sa.Column('performance_average_power_4', sa.Integer(), nullable=True),
    sa.Column('performance_hr_max_4', sa.Integer(), nullable=True),
    sa.Column('recovery_smo2_1', sa.Integer(), nullable=True),
    sa.Column('recovery_thb_1', sa.Integer(), nullable=True),
    sa.Column('recovery_average_power_1', sa.Integer(), nullable=True),
    sa.Column('recovery_hr_min_1', sa.Integer(), nullable=True),
    sa.Column('recovery_smo2_2', sa.Integer(), nullable=True),
    sa.Column('recovery_thb_2', sa.Integer(), nullable=True),
    sa.Column('recovery_average_power_2', sa.Integer(), nullable=True),
    sa.Column('recovery_hr_min_2', sa.Integer(), nullable=True),
    sa.Column('recovery_smo2_3', sa.Integer(), nullable=True),
    sa.Column('recovery_thb_3', sa.Integer(), nullable=True),
    sa.Column('recovery_average_power_3', sa.Integer(), nullable=True),
    sa.Column('recovery_hr_min_3', sa.Integer(), nullable=True),
    sa.Column('recovery_smo2_4', sa.Integer(), nullable=True),
    sa.Column('recovery_thb_4', sa.Integer(), nullable=True),
    sa.Column('recovery_average_power_4', sa.Integer(), nullable=True),
    sa.Column('recovery_hr_min_4', sa.Integer(), nullable=True),
    sa.Column('smo2_tank_size', sa.Integer(), nullable=True),
    sa.Column('thb_tank_size', sa.Integer(), nullable=True),
    sa.Column('performance_baseline_smo2', sa.Integer(), nullable=True),
    sa.Column('performance_baseline_thb', sa.Integer(), nullable=True),
    sa.Column('recovery_baseline_smo2', sa.Integer(), nullable=True),
    sa.Column('recovery_baseline_thb', sa.Integer(), nullable=True),
    sa.Column('avg_watt_kg', sa.Float(), nullable=True),
    sa.Column('avg_interval_time', sa.Integer(), nullable=True),
    sa.Column('avg_recovery_time', sa.Integer(), nullable=True),
    sa.Column('limiter', sa.String(), nullable=True),
    sa.Column('intervention', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='moxy_rip_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TrainerPowerAssessment',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('keiser_upper_r_weight', sa.Integer(), nullable=True),
    sa.Column('keiser_upper_r_attempt_1', sa.Integer(), nullable=True),
    sa.Column('keiser_upper_r_attempt_2', sa.Integer(), nullable=True),
    sa.Column('keiser_upper_r_attempt_3', sa.Integer(), nullable=True),
    sa.Column('keiser_upper_l_weight', sa.Integer(), nullable=True),
    sa.Column('keiser_upper_l_attempt_1', sa.Integer(), nullable=True),
    sa.Column('keiser_upper_l_attempt_2', sa.Integer(), nullable=True),
    sa.Column('keiser_upper_l_attempt_3', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_bi_weight', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_bi_attempt_1', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_bi_attempt_2', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_bi_attempt_3', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_r_weight', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_r_attempt_1', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_r_attempt_2', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_r_attempt_3', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_l_weight', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_l_attempt_1', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_l_attempt_2', sa.Integer(), nullable=True),
    sa.Column('keiser_lower_l_attempt_3', sa.Integer(), nullable=True),
    sa.Column('upper_watts_per_kg', sa.Float(), nullable=True),
    sa.Column('lower_watts_per_kg', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='power_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('TrainerStrengthAssessment',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('upper_push_notes', sa.Text(), nullable=True),
    sa.Column('upper_pull_notes', sa.Text(), nullable=True),
    sa.Column('upper_push_l_weight', sa.Integer(), nullable=True),
    sa.Column('upper_push_l_attempt_1', sa.Integer(), nullable=True),
    sa.Column('upper_push_l_attempt_2', sa.Integer(), nullable=True),
    sa.Column('upper_push_l_attempt_3', sa.Integer(), nullable=True),
    sa.Column('upper_push_l_estimated_10rm', sa.Float(), nullable=True),
    sa.Column('upper_push_r_weight', sa.Integer(), nullable=True),
    sa.Column('upper_push_r_attempt_1', sa.Integer(), nullable=True),
    sa.Column('upper_push_r_attempt_2', sa.Integer(), nullable=True),
    sa.Column('upper_push_r_attempt_3', sa.Integer(), nullable=True),
    sa.Column('upper_push_r_estimated_10rm', sa.Float(), nullable=True),
    sa.Column('upper_push_bi_weight', sa.Integer(), nullable=True),
    sa.Column('upper_push_bi_attempt_1', sa.Integer(), nullable=True),
    sa.Column('upper_push_bi_attempt_2', sa.Integer(), nullable=True),
    sa.Column('upper_push_bi_attempt_3', sa.Integer(), nullable=True),
    sa.Column('upper_push_bi_estimated_10rm', sa.Float(), nullable=True),
    sa.Column('upper_pull_l_weight', sa.Integer(), nullable=True),
    sa.Column('upper_pull_l_attempt_1', sa.Integer(), nullable=True),
    sa.Column('upper_pull_l_attempt_2', sa.Integer(), nullable=True),
    sa.Column('upper_pull_l_attempt_3', sa.Integer(), nullable=True),
    sa.Column('upper_pull_l_estimated_10rm', sa.Float(), nullable=True),
    sa.Column('upper_pull_r_weight', sa.Integer(), nullable=True),
    sa.Column('upper_pull_r_attempt_1', sa.Integer(), nullable=True),
    sa.Column('upper_pull_r_attempt_2', sa.Integer(), nullable=True),
    sa.Column('upper_pull_r_attempt_3', sa.Integer(), nullable=True),
    sa.Column('upper_pull_r_estimated_10rm', sa.Float(), nullable=True),
    sa.Column('upper_pull_bi_weight', sa.Integer(), nullable=True),
    sa.Column('upper_pull_bi_attempt_1', sa.Integer(), nullable=True),
    sa.Column('upper_pull_bi_attempt_2', sa.Integer(), nullable=True),
    sa.Column('upper_pull_bi_attempt_3', sa.Integer(), nullable=True),
    sa.Column('upper_pull_bi_estimated_10rm', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='strength_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.drop_table('strength_assessment')
    op.drop_table('moxy_assessment')
    op.drop_table('moxy_rip_test')
    op.drop_table('power_assessment')
    op.drop_table('heart_assessment')
    op.drop_index('ix_remote_registration_registration_portal_id', table_name='remote_registration')
    op.drop_index('ix_remote_registration_token', table_name='remote_registration')
    op.drop_table('remote_registration')
    op.drop_table('chessboard')
    op.drop_table('lung_assessment')
    op.drop_table('client_removal_requests')
    op.drop_table('movement_assessment')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('movement_assessment',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('squat_dept', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('squat_ramp', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('squat_eye_test', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('squat_can_breathe', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('squat_can_look_up', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('toe_touch_depth', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('toe_touch_pelvis_movement', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('toe_touch_ribcage_movement', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('toe_touch_notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('standing_rotation_r_notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('standing_rotation_l_notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='movement_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='movement_assessment_pkey')
    )
    op.create_table('client_removal_requests',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('staffid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['staffid'], ['Staff.staffid'], name='ClientRemovalRequests_staffid_fkey'),
    sa.PrimaryKeyConstraint('idx', name='client_removal_requests_pkey')
    )
    op.create_table('lung_assessment',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('bag_size', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('duration', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('breaths_per_minute', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('max_minute_volume', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('liters_min_kg', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='lung_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='lung_assessment_pkey')
    )
    op.create_table('chessboard',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('isa_right', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('isa_left', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('isa_structure', sa.VARCHAR(length=24), autoincrement=False, nullable=True),
    sa.Column('isa_dynamic', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('left_shoulder_er', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_shoulder_ir', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_shoulder_abd', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_shoulder_add', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_shoulder_flexion', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_shoulder_extension', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_shoulder_er', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_shoulder_ir', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_shoulder_abd', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_shoulder_add', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_shoulder_flexion', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_shoulder_extension', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_hip_slr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_hip_er', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_hip_ir', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_hip_abd', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_hip_add', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_hip_flexion', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('left_hip_extension', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_hip_er', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_hip_ir', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_hip_abd', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_hip_add', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_hip_flexion', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_hip_extension', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('right_hip_slr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='chessboard_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='chessboard_pkey')
    )
    op.create_table('remote_registration',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('token', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('token_expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('password', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('registration_portal_id', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('registration_portal_expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='remote_registration_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='remote_registration_pkey')
    )
    op.create_index('ix_remote_registration_token', 'remote_registration', ['token'], unique=True)
    op.create_index('ix_remote_registration_registration_portal_id', 'remote_registration', ['registration_portal_id'], unique=True)
    op.create_table('heart_assessment',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('resting_hr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('max_hr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('theoretical_max_hr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('avg_eval_hr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('avg_training_hr', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('estimated_vo2_max', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='heart_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='heart_assessment_pkey')
    )
    op.create_table('power_assessment',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('keiser_upper_r_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_upper_r_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_upper_r_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_upper_r_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_upper_l_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_upper_l_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_upper_l_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_upper_l_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_bi_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_bi_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_bi_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_bi_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_r_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_r_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_r_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_r_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_l_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_l_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_l_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keiser_lower_l_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_watts_per_kg', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('lower_watts_per_kg', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='power_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='power_assessment_pkey')
    )
    op.create_table('moxy_rip_test',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('performance_smo2_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_thb_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_average_power_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_hr_max_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_smo2_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_thb_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_average_power_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_hr_max_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_smo2_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_thb_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_average_power_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_hr_max_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_smo2_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_thb_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_average_power_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_hr_max_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_smo2_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_thb_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_average_power_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_hr_min_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_smo2_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_thb_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_average_power_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_hr_min_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_smo2_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_thb_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_average_power_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_hr_min_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_smo2_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_thb_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_average_power_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_hr_min_4', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('smo2_tank_size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('thb_tank_size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_baseline_smo2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_baseline_thb', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_baseline_smo2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recovery_baseline_thb', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('avg_watt_kg', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('avg_interval_time', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('avg_recovery_time', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('limiter', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('intervention', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='moxy_rip_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='moxy_rip_test_pkey')
    )
    op.create_table('moxy_assessment',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('recovery_baseline', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_baseline', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('gas_tank_size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('starting_sm_o2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('starting_thb', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('limiter', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('intervention', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('performance_metric_1', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('performance_metric_1_value', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('performance_metric_2', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('performance_metric_2_value', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='moxy_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='moxy_assessment_pkey')
    )
    op.create_table('strength_assessment',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('clientid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('upper_push_notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('upper_push_l_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_l_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_l_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_l_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_l_estimated_10rm', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('upper_push_r_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_r_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_r_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_r_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_r_estimated_10rm', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('upper_push_bi_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_bi_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_bi_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_bi_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_push_bi_estimated_10rm', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('upper_pull_l_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_l_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_l_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_l_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_l_estimated_10rm', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('upper_pull_r_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_r_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_r_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_r_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_r_estimated_10rm', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('upper_pull_bi_weight', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_bi_attempt_1', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_bi_attempt_2', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_bi_attempt_3', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upper_pull_bi_estimated_10rm', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='strength_assessment_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='strength_assessment_pkey')
    )
    op.drop_table('TrainerStrengthAssessment')
    op.drop_table('TrainerPowerAssessment')
    op.drop_table('TrainerMoxyRipTest')
    op.drop_table('TrainerMoxyAssessment')
    op.drop_table('TrainerMovementAssessment')
    op.drop_table('TrainerLungAssessment')
    op.drop_table('TrainerHeartAssessment')
    op.drop_table('PTChessboard')
    op.drop_table('ClientRemovalRequests')
    op.drop_index(op.f('ix_ClientRemoteRegistration_token'), table_name='ClientRemoteRegistration')
    op.drop_index(op.f('ix_ClientRemoteRegistration_registration_portal_id'), table_name='ClientRemoteRegistration')
    op.drop_table('ClientRemoteRegistration')
    # ### end Alembic commands ###
