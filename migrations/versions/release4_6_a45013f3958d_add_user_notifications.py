"""add user notifications

Revision ID: a45013f3958d
Revises: e21ae83791f6
Create Date: 2021-01-29 16:54:36.542761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a45013f3958d'
down_revision = 'e21ae83791f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupNotifications',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('notification_type_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('notification_type', sa.String(), nullable=True),
    sa.Column('icon', sa.String(), nullable=True),
    sa.Column('background_color', sa.String(), nullable=True),
    sa.Column('symbol_color', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('notification_type_id')
    )
    op.create_table('UserNotifications',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('notification_type_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('action', sa.String(), nullable=True),
    sa.Column('time_to_live', sa.DateTime(), nullable=True),
    sa.Column('is_staff', sa.Boolean(), nullable=True),
    sa.Column('read', sa.Boolean(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['notification_type_id'], ['LookupNotifications.notification_type_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UserNotifications')
    op.drop_table('LookupNotifications')
    # ### end Alembic commands ###
