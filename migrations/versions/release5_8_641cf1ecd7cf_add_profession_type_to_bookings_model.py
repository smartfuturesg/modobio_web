"""add profession_type to bookings model

Revision ID: 641cf1ecd7cf
Revises: 9e0726f03478
Create Date: 2021-04-09 12:09:08.572797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '641cf1ecd7cf'
down_revision = '9e0726f03478'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TelehealthBookings', sa.Column('profession_type', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TelehealthBookings', 'profession_type')
    # ### end Alembic commands ###
