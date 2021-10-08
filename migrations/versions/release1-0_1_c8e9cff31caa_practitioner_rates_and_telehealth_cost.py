"""practitioner rates, telehealth bookings consult rate

Revision ID: c8e9cff31caa
Revises: 0bebaad7e4a1
Create Date: 2021-10-04 12:00:13.171745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8e9cff31caa'
down_revision = 'a6162914753b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('LookupCurrencies', sa.Column('increment', sa.Integer(), nullable=True))
    op.add_column('LookupCurrencies', sa.Column('max_rate', sa.Float(), nullable=True))
    op.add_column('LookupCurrencies', sa.Column('min_rate', sa.Float(), nullable=True))
    op.add_column('StaffRoles', sa.Column('consult_rate', sa.Float(), nullable=True))
    op.add_column('TelehealthBookings', sa.Column('consult_rate', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TelehealthBookings', 'consult_rate')
    op.drop_column('StaffRoles', 'consult_rate')
    op.drop_column('LookupCurrencies', 'min_rate')
    op.drop_column('LookupCurrencies', 'max_rate')
    op.drop_column('LookupCurrencies', 'increment')
    # ### end Alembic commands ###
