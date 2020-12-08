"""add UserSubscriptions table

Revision ID: 56b2a6e68f94
Revises: 40e57e2da26a
Create Date: 2020-12-08 11:29:19.158136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56b2a6e68f94'
down_revision = '40e57e2da26a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserSubscriptions',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('is_staff', sa.Boolean(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('subscription_rate', sa.Float(), nullable=True),
    sa.Column('subscription_type', sa.Enum('unsubscribed', 'subscribed', 'free_trial', 'sponsored', name='subtypes'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'is_staff')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UserSubscriptions')
    # ### end Alembic commands ###
