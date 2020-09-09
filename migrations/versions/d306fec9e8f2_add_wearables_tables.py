"""add wearables tables

Revision ID: d306fec9e8f2
Revises: c9c14471cbd4
Create Date: 2020-08-11 17:09:58.148479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd306fec9e8f2'
down_revision = 'c9c14471cbd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Wearables',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('has_oura', sa.Boolean(), nullable=False),
    sa.Column('registered_oura', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_table('WearablesOura',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('clientid', sa.Integer(), nullable=False),
    sa.Column('oauth_state', sa.String(length=50), nullable=True)
    sa.Column('grant_token', sa.String(length=50), nullable=True),
    sa.Column('access_token', sa.String(length=50), nullable=True),
    sa.Column('refresh_token', sa.String(length=50), nullable=True),
    sa.Column('token_expires', sa.DateTime(), nullable=True),
    sa.Column('last_scrape', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['clientid'], ['ClientInfo.clientid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('WearablesOura')
    op.drop_table('Wearables')
    # ### end Alembic commands ###
