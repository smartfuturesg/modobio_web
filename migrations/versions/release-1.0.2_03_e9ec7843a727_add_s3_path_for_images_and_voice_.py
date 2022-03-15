"""Add S3 path for images and voice recording to TelehealthBookingDetails

Revision ID: e9ec7843a727
Revises: deaa74c44845
Create Date: 2022-03-15 13:19:34.057949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9ec7843a727'
down_revision = 'deaa74c44845'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'TelehealthBookingDetails',
        sa.Column(
            'images',
            sa.ARRAY(
                sa.String(length=1024),
                dimensions=1),
            nullable=True))
    op.add_column(
        'TelehealthBookingDetails',
        sa.Column(
            'voice',
            sa.String(length=1024),
            nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TelehealthBookingDetails', 'voice')
    op.drop_column('TelehealthBookingDetails', 'images')
    # ### end Alembic commands ###
