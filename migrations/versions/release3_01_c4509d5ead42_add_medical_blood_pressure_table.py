"""add medical blood pressure table

Revision ID: c4509d5ead42
Revises: d4b6966523ba
Create Date: 2020-12-25 10:28:37.260256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4509d5ead42'
down_revision = 'd4b6966523ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MedicalBloodPressures',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('systolic', sa.Float(), nullable=True),
    sa.Column('diastolic', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('MedicalBloodPressures')
    # ### end Alembic commands ###
