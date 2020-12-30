"""look up activity tracker

Revision ID: 60c7a4ef3c9a
Revises: d4b6966523ba
Create Date: 2020-12-26 10:47:10.807343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60c7a4ef3c9a'
down_revision = 'c4509d5ead42'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupActivityTrackers',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('brand', sa.String(), nullable=True),
    sa.Column('series', sa.String(), nullable=True),
    sa.Column('model', sa.String(), nullable=True),
    sa.Column('ecg_metric_1', sa.Boolean(), nullable=True),
    sa.Column('ecg_metric_2', sa.Boolean(), nullable=True),
    sa.Column('sp_o2_spot_check', sa.Boolean(), nullable=True),
    sa.Column('sp_o2_nighttime_avg', sa.Boolean(), nullable=True),
    sa.Column('sleep_total', sa.Boolean(), nullable=True),
    sa.Column('deep_sleep', sa.Boolean(), nullable=True),
    sa.Column('rem_sleep', sa.Boolean(), nullable=True),
    sa.Column('quality_sleep', sa.Boolean(), nullable=True),
    sa.Column('light_sleep', sa.Boolean(), nullable=True),
    sa.Column('awake', sa.Boolean(), nullable=True),
    sa.Column('sleep_latency', sa.Boolean(), nullable=True),
    sa.Column('bedtime_consistency', sa.Boolean(), nullable=True),
    sa.Column('wake_consistency', sa.Boolean(), nullable=True),
    sa.Column('rhr_avg', sa.Boolean(), nullable=True),
    sa.Column('rhr_lowest', sa.Boolean(), nullable=True),
    sa.Column('hr_walking', sa.Boolean(), nullable=True),
    sa.Column('hr_24hr_avg', sa.Boolean(), nullable=True),
    sa.Column('hrv_avg', sa.Boolean(), nullable=True),
    sa.Column('body_temperature', sa.Boolean(), nullable=True),
    sa.Column('steps', sa.Boolean(), nullable=True),
    sa.Column('total_calories', sa.Boolean(), nullable=True),
    sa.Column('active_calories', sa.Boolean(), nullable=True),
    sa.Column('walking_equivalency', sa.Boolean(), nullable=True),
    sa.Column('inactivity', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LookupActivityTrackers')
    # ### end Alembic commands ###
