"""medical credentials

Revision ID: aabbac2cfa80
Revises: a2b1226364ee
Create Date: 2021-08-09 11:37:34.190785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aabbac2cfa80'
down_revision = 'a2b1226364ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MedicalCredentials',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('territory', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('credential_type', sa.String(), nullable=True),
    sa.Column('medical_doctor_credentials', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('MedicalCredentials')
    # ### end Alembic commands ###
