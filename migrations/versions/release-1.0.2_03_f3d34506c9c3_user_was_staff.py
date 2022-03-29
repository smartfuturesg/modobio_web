"""Make User.was_staff not nullable

Revision ID: f3d34506c9c3
Revises: deaa74c44845
Create Date: 2022-03-18 11:43:57.510596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3d34506c9c3'
down_revision = 'deaa74c44845'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'was_staff',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'was_staff',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
