"""User.is_provider flag

Revision ID: 3669c98b6396
Revises: a2cd76a0affa
Create Date: 2022-10-24 13:27:45.370664

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3669c98b6396'
down_revision = 'a2cd76a0affa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('User', sa.Column('is_provider', sa.Boolean(), server_default='false', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'is_provider')
   
    # ### end Alembic commands ###
