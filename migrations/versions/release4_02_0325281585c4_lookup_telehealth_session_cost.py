"""lookup telehealth session cost

Revision ID: 0325281585c4
Revises: 5a0ae7ad37d1
Create Date: 2021-01-06 06:58:02.538623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0325281585c4'
down_revision = '22fcb8ff2a65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupTelehealthSessionCost',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('profession_type', sa.String(), nullable=True),
    sa.Column('territory', sa.String(), nullable=True),
    sa.Column('session_cost', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('idx')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LookupTelehealthSessionCost')
    # ### end Alembic commands ###
