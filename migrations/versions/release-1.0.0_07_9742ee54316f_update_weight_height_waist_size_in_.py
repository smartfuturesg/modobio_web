"""Update weight, height, waist_size in ClientInfo to Numeric type.

Revision ID: 9742ee54316f
Revises: edc81a136dc8
Create Date: 2021-11-17 17:29:21.813620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9742ee54316f'
down_revision = 'edc81a136dc8'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('ClientInfo', 'height', type_=sa.Numeric(precision=10, scale=6, asdecimal=False))
    op.alter_column('ClientInfo', 'waist_size', type_=sa.Numeric(precision=10, scale=6, asdecimal=False))

    # Temporarily give this more precision than needed, to deal with g -> kg conversion.
    op.alter_column('ClientInfo', 'weight', type_=sa.Numeric(precision=20, scale=11, asdecimal=False))

    op.execute('UPDATE "ClientInfo" SET weight = weight / 1000 WHERE weight > 1000;')

    # Reduce precision to what is defined in model.
    op.alter_column('ClientInfo', 'weight', type_=sa.Numeric(precision=15, scale=11, asdecimal=False))

def downgrade():
    # Temporarily give this more precision than needed, to deal with kg -> g conversion.
    op.alter_column('ClientInfo', 'weight', type_=sa.Numeric(precision=20, scale=11, asdecimal=False))

    op.execute('UPDATE "ClientInfo" SET weight = weight * 1000 WHERE weight < 1000;')

    # Conversion back to integer rounds.
    op.alter_column('ClientInfo', 'weight', type_=sa.INTEGER())

    op.alter_column('ClientInfo', 'waist_size', type_=sa.INTEGER())
    op.alter_column('ClientInfo', 'height', type_=sa.INTEGER())
