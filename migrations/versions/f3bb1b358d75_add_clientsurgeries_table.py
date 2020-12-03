"""add ClientSurgeries table

Revision ID: f3bb1b358d75
Revises: 04ea7e0894a4
Create Date: 2020-11-23 09:39:11.219861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3bb1b358d75'
down_revision = '04ea7e0894a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ClientSurgeries',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('surgery_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_user_id', sa.Integer(), nullable=False),
    sa.Column('reporter_user_id', sa.Integer(), nullable=False),
    sa.Column('surgery_category', sa.String(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('surgeon', sa.String(), nullable=True),
    sa.Column('institution', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporter_user_id'], ['User.user_id'], ),
    sa.PrimaryKeyConstraint('surgery_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ClientSurgeries')
    # ### end Alembic commands ###
