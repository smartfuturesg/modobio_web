"""Adds google_transaction_id to UserSubscriptions

Revision ID: ad69ba8f705b
Revises: b26e574b59f8
Create Date: 2023-06-16 12:17:14.821325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad69ba8f705b'
down_revision = 'b26e574b59f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('UserSubscriptions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_transaction_id', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('UserSubscriptions', schema=None) as batch_op:
        batch_op.drop_column('google_transaction_id')

    # ### end Alembic commands ###
