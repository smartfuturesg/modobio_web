"""Allow longer reporter_role & Save video room sid

Revision ID: bd3dcbbe533b
Revises: 08e4c602da79
Create Date: 2021-10-20 11:33:19.071899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd3dcbbe533b'
down_revision = '08e4c602da79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('TelehealthBookingStatus', 'reporter_role',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=30),
               existing_nullable=True)
    op.add_column('TelehealthMeetingRooms', sa.Column('sid', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TelehealthMeetingRooms', 'sid')
    op.alter_column('TelehealthBookingStatus', 'reporter_role',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    # ### end Alembic commands ###
