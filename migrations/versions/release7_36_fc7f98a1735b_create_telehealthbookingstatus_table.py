"""Create TelehealthBookingStatus table

Revision ID: fc7f98a1735b
Revises: b76c62d0757d
Create Date: 2021-08-13 17:40:10.641232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc7f98a1735b'
down_revision = 'b76c62d0757d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TelehealthBookingStatus',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('reporter_role', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('time', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('reporter_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['booking_id'], ['TelehealthBookings.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporter_id'], ['User.user_id'], ),
    sa.PrimaryKeyConstraint('idx')
    )
    op.alter_column('TelehealthBookings', 'target_date',
               existing_type=sa.DATE(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('TelehealthBookings', 'target_date',
               existing_type=sa.DATE(),
               nullable=True)
    op.drop_table('TelehealthBookingStatus')
    # ### end Alembic commands ###
