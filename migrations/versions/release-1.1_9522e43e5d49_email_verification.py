"""Adds email field to UserPendingEmailVerifications

Revision ID: 9522e43e5d49
Revises: fb14f8b40f12
Create Date: 2022-01-10 12:14:44.076869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9522e43e5d49'
down_revision = 'fb14f8b40f12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('UserPendingEmailVerifications', sa.Column('email', sa.String(length=75), nullable=True))
    op.create_unique_constraint(None, 'UserPendingEmailVerifications', ['user_id'])
    op.create_unique_constraint(None, 'UserPendingEmailVerifications', ['email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'UserPendingEmailVerifications', type_='unique')
    op.drop_constraint(None, 'UserPendingEmailVerifications', type_='unique')
    op.drop_column('UserPendingEmailVerifications', 'email')
    # ### end Alembic commands ###
