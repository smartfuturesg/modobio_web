"""Add field to UserSubscriptions

Revision ID: 7d0ff5d59641
Revises: e3f798f467ca
Create Date: 2023-06-21 15:48:17.541979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7d0ff5d59641"
down_revision = "e3f798f467ca"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("UserSubscriptions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("apple_auto_renew", sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("UserSubscriptions", schema=None) as batch_op:
        batch_op.drop_column("apple_auto_renew")

    # ### end Alembic commands ###
