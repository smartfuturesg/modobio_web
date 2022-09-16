"""empty message

Revision ID: 09bd96cf3eb5
Revises: c3cfeb49a26e
Create Date: 2022-09-14 12:59:18.559625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09bd96cf3eb5'
down_revision = 'c3cfeb49a26e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('MedicalBloodTests', sa.Column('was_fasted', sa.Boolean(), nullable=True))
    op.drop_column('MedicalBloodTests', 'panel_type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('MedicalBloodTests', sa.Column('panel_type', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('MedicalBloodTests', 'was_fasted')
    # ### end Alembic commands ###
