"""add system telehealth settings

Revision ID: c201ba5bf77d
Revises: a45013f3958d
Create Date: 2021-02-09 14:38:05.862952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c201ba5bf77d'
down_revision = 'a45013f3958d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('SystemTelehealthSessionCosts',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('territory_id', sa.Integer(), nullable=False),
    sa.Column('profession_type', sa.String(), nullable=False),
    sa.Column('session_cost', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['territory_id'], ['LookupCountriesOfOperations.idx'], ),
    sa.PrimaryKeyConstraint('territory_id', 'profession_type')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('SystemTelehealthSessionCosts')
    # ### end Alembic commands ###
