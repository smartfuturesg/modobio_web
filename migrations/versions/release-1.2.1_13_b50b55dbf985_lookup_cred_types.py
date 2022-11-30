"""Tables created:
- LookupCredentialTypes

Revision ID: b50b55dbf985
Revises: 8ccdd1fa402a
Create Date: 2022-11-30 10:54:24.268732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b50b55dbf985'
down_revision = '8ccdd1fa402a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupCredentialTypes',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('credential_type', sa.String(), nullable=True),
    sa.Column('display_name', sa.String(), nullable=True),
    sa.Column('country_required', sa.Boolean(), nullable=True),
    sa.Column('sub_territory_required', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('idx'),
    sa.UniqueConstraint('credential_type')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LookupCredentialTypes')
    # ### end Alembic commands ###
