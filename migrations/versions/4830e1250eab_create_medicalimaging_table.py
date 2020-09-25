"""Create MedicalImaging Table

Revision ID: 4830e1250eab
Revises: 9887fc6db28e
Create Date: 2020-09-21 15:22:59.531096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4830e1250eab'
down_revision = '3cb25c724f84'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MedicalImaging',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('image_date', sa.DateTime(), nullable=True),
    sa.Column('image_type', sa.String(length=1024), nullable=True),
    sa.Column('image_read', sa.Text(), nullable=True),
    sa.Column('image_origin_location', sa.Text(), nullable=True),
    sa.Column('image_path', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('MedicalImaging')
    # ### end Alembic commands ###
