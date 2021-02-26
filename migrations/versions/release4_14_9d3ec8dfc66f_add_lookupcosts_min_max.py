"""Add LookupCosts min max

Revision ID: 9d3ec8dfc66f
Revises: c53609fb5b6f
Create Date: 2021-03-01 08:18:19.281226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d3ec8dfc66f'
down_revision = 'c53609fb5b6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('LookupTelehealthSessionCost', sa.Column('session_max_cost', sa.Float(), nullable=True))
    op.add_column('LookupTelehealthSessionCost', sa.Column('session_min_cost', sa.Float(), nullable=True))
    op.drop_column('LookupTelehealthSessionCost', 'session_cost')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('LookupTelehealthSessionCost', sa.Column('session_cost', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('LookupTelehealthSessionCost', 'session_min_cost')
    op.drop_column('LookupTelehealthSessionCost', 'session_max_cost')
    # ### end Alembic commands ###
