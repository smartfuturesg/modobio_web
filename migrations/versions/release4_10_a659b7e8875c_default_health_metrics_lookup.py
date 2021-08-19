"""Default health metrics lookup table

Revision ID: a659b7e8875c
Revises: a45013f3958d
Create Date: 2021-02-11 12:02:41.966441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a659b7e8875c'
down_revision = 'e8cb26a9db4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupDefaultHealthMetrics',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('sex', sa.String(length=2), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('bmi_underweight', sa.Float(), nullable=True),
    sa.Column('bmi_normal_min', sa.Float(), nullable=True),
    sa.Column('bmi_normal_max', sa.Float(), nullable=True),
    sa.Column('bmi_overweight_min', sa.Float(), nullable=True),
    sa.Column('bmi_overweight_max', sa.Float(), nullable=True),
    sa.Column('bmi_obese', sa.Float(), nullable=True),
    sa.Column('ecg_metric_1', sa.String(), nullable=True),
    sa.Column('ecg_metric_2_bpm_min', sa.Integer(), nullable=True),
    sa.Column('ecg_metric_2_bpm_max', sa.Integer(), nullable=True),
    sa.Column('sp_o2_spot_check', sa.Integer(), nullable=True),
    sa.Column('sp_o2_nighttime_avg', sa.Integer(), nullable=True),
    sa.Column('sleep_total_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_deep_min_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_deep_max_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_rem_min_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_rem_max_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_quality_min_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_quality_max_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_light_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_time_awake_minutes', sa.Integer(), nullable=True),
    sa.Column('sleep_latency_minutes', sa.Integer(), nullable=True),
    sa.Column('bedtime_consistency_minutes', sa.Integer(), nullable=True),
    sa.Column('wake_consistency_minutes', sa.Integer(), nullable=True),
    sa.Column('heart_rate_rest_average_min', sa.Integer(), nullable=True),
    sa.Column('heart_rate_rest_average_max', sa.Integer(), nullable=True),
    sa.Column('heart_rate_rest_lowest_min', sa.Integer(), nullable=True),
    sa.Column('heart_rate_rest_lowest_max', sa.Integer(), nullable=True),
    sa.Column('heart_rate_walking_min', sa.Integer(), nullable=True),
    sa.Column('heart_rate_walking_max', sa.Integer(), nullable=True),
    sa.Column('heart_rate_average_min', sa.Integer(), nullable=True),
    sa.Column('heart_rate_average_max', sa.Integer(), nullable=True),
    sa.Column('heart_rate_variability_average_milliseconds', sa.Integer(), nullable=True),
    sa.Column('heart_rate_variability_highest_milliseconds', sa.Integer(), nullable=True),
    sa.Column('respiratory_rate_min_per_minute', sa.Integer(), nullable=True),
    sa.Column('respiratory_rate_max_per_minute', sa.Integer(), nullable=True),
    sa.Column('body_temperature_deviation_fahrenheit', sa.Float(), nullable=True),
    sa.Column('steps_per_day', sa.Integer(), nullable=True),
    sa.Column('steps_walking_equivalency_miles', sa.Integer(), nullable=True),
    sa.Column('calories_total', sa.Integer(), nullable=True),
    sa.Column('calories_active_burn_min', sa.Integer(), nullable=True),
    sa.Column('calories_active_burn_max', sa.Integer(), nullable=True),
    sa.Column('inactivity_minutes', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('idx')
    )



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LookupDefaultHealthMetrics')
    # ### end Alembic commands ###
