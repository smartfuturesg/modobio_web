"""add telehealth booking increments

Revision ID: 342bfe80cc99
Revises: 0a355c29b670
Create Date: 2021-03-12 12:15:19.289430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '342bfe80cc99'
down_revision = '0a355c29b670'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupBookingTimeIncrements',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LookupBookingTimeIncrements')
    # ### end Alembic commands ###
