"""added MedicalBloodChemistryLipids table

Revision ID: 644674db8df8
Revises: c9c14471cbd4
Create Date: 2020-09-04 16:01:03.899726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '644674db8df8'
down_revision = 'c9c14471cbd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MedicalBloodChemistryLipids',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('exam_date', sa.Date(), nullable=True),
    sa.Column('cholesterol_total', sa.Integer(), nullable=True),
    sa.Column('cholesterol_ldl', sa.Integer(), nullable=True),
    sa.Column('cholesterol_hdl', sa.Integer(), nullable=True),
    sa.Column('triglycerides', sa.Integer(), nullable=True),
    sa.Column('cholesterol_over_hdl', sa.Float(), nullable=True),
    sa.Column('triglycerides_over_hdl', sa.Float(), nullable=True),
    sa.Column('ldl_over_hdl', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='BloodThyroid_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('MedicalBloodChemistryLipids')
    # ### end Alembic commands ###
