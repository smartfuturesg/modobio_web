"""Add ClientPushNotifications table

Revision ID: f56c6155f65c
Revises: d7cf0daaee91
Create Date: 2021-03-22 08:22:14.511241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f56c6155f65c'
down_revision = '60a0292ebacb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ClientPushNotifications',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('notification_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['notification_type_id'], ['LookupNotifications.notification_type_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ClientPushNotifications')
    # ### end Alembic commands ###
