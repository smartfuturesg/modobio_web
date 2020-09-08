"""Added MedicalBloodChemistryA1C table

Revision ID: 313c27dafb4d
Revises: c8334dc2c01f
Create Date: 2020-09-08 13:14:40.821849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '313c27dafb4d'
down_revision = 'c8334dc2c01f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MedicalBloodChemistryA1C',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('exam_date', sa.Date(), nullable=True),
    sa.Column('a1c', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], name='BloodA1C_clientid_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('MedicalBloodChemistryA1C')
    # ### end Alembic commands ###
