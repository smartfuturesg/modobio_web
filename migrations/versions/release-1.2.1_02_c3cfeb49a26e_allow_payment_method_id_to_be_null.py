"""Allow payment_method_id to be null

Revision ID: c3cfeb49a26e
Revises: b9131229632d
Create Date: 2022-09-01 16:58:52.541202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3cfeb49a26e'
down_revision = 'a8c8b8ed2cd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('TelehealthBookings', 'payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('TelehealthQueueClientPool', 'payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('TelehealthQueueClientPool', 'payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('TelehealthBookings', 'payment_method_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
