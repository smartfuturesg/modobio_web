"""Add LookupRaces table

Revision ID: 651640b15d14
Revises: 91bf7a4c4aba
Create Date: 2021-01-08 11:44:52.192054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '651640b15d14'
down_revision = '91bf7a4c4aba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupRaces',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('race_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('race_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('race_id')
    )
    op.add_column('ClientInfo', sa.Column('race_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'ClientInfo', 'LookupRaces', ['race_id'], ['race_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ClientInfo', type_='foreignkey')
    op.drop_column('ClientInfo', 'race_id')
    op.drop_table('LookupRaces')
    # ### end Alembic commands ###
