"""Add write access timeout to TelehealthChatRooms

Revision ID: a08e5794c7ec
Revises: c708e6669220
Create Date: 2021-11-23 11:41:52.116737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a08e5794c7ec'
down_revision = 'c708e6669220'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TelehealthChatRooms', sa.Column('write_access_timeout', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TelehealthChatRooms', 'write_access_timeout')
    # ### end Alembic commands ###
