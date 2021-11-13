"""Change height, weight, waist from int to numeric.
Change tablenames to drop -History postfix.
Change data in weight column from g to kg.

Revision ID: edc81a136dc8
Revises: aa9b5a000691
Create Date: 2021-11-12 15:04:43.281446

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'edc81a136dc8'
down_revision = 'aa9b5a000691'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('ClientHeightHistory', 'ClientHeight')
    op.rename_table('ClientWeightHistory', 'ClientWeight')
    op.rename_table('ClientWaistSizeHistory', 'ClientWaistSize')

    op.alter_column('ClientHeight', 'height', type_=sa.Numeric(precision=10, scale=6))
    op.alter_column('ClientWaistSize', 'waist_size', type_=sa.Numeric(precision=10, scale=6))

    # Temporarily give this more precision than needed, to deal with g -> kg conversion.
    op.alter_column('ClientWeight', 'weight', type_=sa.Numeric(precision=20, scale=11))

    # Convert weight in g to kg.
    # Weight in g is always > 1000 g (> 1 kg, even a premature baby weighs more),
    # and weight in kg is never > 1000 kg (heaviest man ever est. peaked at 635 kg).
    # The WHERE clause prevents us from applying this multiple times.
    op.execute('UPDATE "ClientWeight" SET weight = weight / 1000 WHERE weight > 1000;')

    # Reduce precision to what is defined in model.
    op.alter_column('ClientWeight', 'weight', type_=sa.Numeric(precision=15, scale=11))

def downgrade():
    # Temporarily give this more precision than needed, to deal with kg -> g conversion.
    op.alter_column('ClientWeight', 'weight', type_=sa.Numeric(precision=20, scale=11))

    op.execute('UPDATE "ClientWeight" SET weight = weight * 1000 WHERE weight < 1000;')

    # Conversion back to integer rounds.
    op.alter_column('ClientHeight', 'height', type_=sa.Integer)
    op.alter_column('ClientWeight', 'weight', type_=sa.Integer)
    op.alter_column('ClientWaistSize', 'waist_size', type_=Integer)

    op.rename_table('ClientHeight', 'ClientHeightHistory')
    op.rename_table('ClientWeight', 'ClientWeightHistory')
    op.rename_table('ClientWaistSize', 'ClientWaistSizeHistory')
