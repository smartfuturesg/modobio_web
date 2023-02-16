"""Adds fields to lookup roles

Revision ID: 73b9e8b8b4aa
Revises: 91df2cb12fba
Create Date: 2023-02-02 02:16:37.068831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73b9e8b8b4aa'
down_revision = '91df2cb12fba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupRoleGroups',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('group_name', sa.String(), nullable=True),
    sa.Column('group_name_abbreviation', sa.String(), nullable=True),
    sa.Column('role_idx', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_idx'], ['LookupRoles.idx'], ),
    sa.PrimaryKeyConstraint('idx')
    )
    op.add_column('LookupRoles', sa.Column('rpm_enroll', sa.Boolean(), nullable=True))
    op.add_column('LookupRoles', sa.Column('rpm_support', sa.Boolean(), nullable=True))
    op.add_column('LookupRoles', sa.Column('telehealth_access', sa.Boolean(), nullable=True))
    op.drop_column('LookupRoles', 'has_client_data_access')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('LookupRoles', sa.Column('has_client_data_access', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('LookupRoles', 'telehealth_access')
    op.drop_column('LookupRoles', 'rpm_support')
    op.drop_column('LookupRoles', 'rpm_enroll')
    op.drop_table('LookupRoleGroups')
    # ### end Alembic commands ###
