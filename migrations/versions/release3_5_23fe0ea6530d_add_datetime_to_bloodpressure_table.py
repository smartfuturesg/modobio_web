"""add datetime to bloodpressure table

Revision ID: 23fe0ea6530d
Revises: b52d104071ea
Create Date: 2021-02-08 04:35:11.219007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23fe0ea6530d'
down_revision = 'b52d104071ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('MedicalBloodPressures', sa.Column('datetime_taken', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('MedicalBloodPressures', 'datetime_taken')
    # ### end Alembic commands ###
