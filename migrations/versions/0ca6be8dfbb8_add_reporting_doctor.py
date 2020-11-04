"""add reporting doctor

Revision ID: 0ca6be8dfbb8
Revises: 181802f48ef7
Create Date: 2020-10-31 11:47:46.212011

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0ca6be8dfbb8'
down_revision = '181802f48ef7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('MedicalPhysicalExam', sa.Column('reporter_id', sa.Integer(), nullable=True))
    op.add_column('MedicalImaging', sa.Column('reporter_id', sa.Integer(), nullable=True))
    op.add_column('MedicalBloodTests', sa.Column('reporter_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('MedicalPhysicalExam', 'reporter_id')
    op.drop_column('MedicalBloodTests', 'reporter_id')
    op.drop_column('MedicalImaging', 'reporter_id')
    # ### end Alembic commands ###
