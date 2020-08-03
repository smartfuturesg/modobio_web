"""
Add access_roles field to staff table. This is an array field.

Revision ID: 5216c031bfd8
Revises: 244d58c0d510
Create Date: 2020-07-31 14:55:15.942505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5216c031bfd8'
down_revision = '244d58c0d510'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Staff', sa.Column('access_roles', sa.ARRAY(sa.String()), server_default='{}', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Staff', 'access_roles')
    # ### end Alembic commands ###
