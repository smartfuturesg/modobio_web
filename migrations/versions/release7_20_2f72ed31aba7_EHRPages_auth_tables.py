"""EHR page auth tables

Revision ID: 2f72ed31aba7
Revises: 1757ded21a69
Create Date: 2021-06-23 16:10:46.493439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f72ed31aba7'
down_revision = '1757ded21a69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupEHRPages',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('resource_group_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('resource_group_name', sa.String(), nullable=True),
    sa.Column('display_name', sa.String(), nullable=True),
    sa.Column('access_group', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('resource_group_id')
    )
    op.add_column('LookupClinicalCareTeamResources', sa.Column('resource_group_id', sa.Integer(), nullable=False))
    op.create_foreign_key('LookupEHR_resource_group_id_fk', 'LookupClinicalCareTeamResources', 'LookupEHRPages', ['resource_group_id'], ['resource_group_id'], ondelete='CASCADE')

    op.create_table('ClientEHRPageAuthorizations',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('team_member_user_id', sa.Integer(), nullable=False),
    sa.Column('resource_group_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['resource_group_id'], ['LookupEHRPages.resource_group_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['team_member_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx'),
    sa.UniqueConstraint('user_id', 'team_member_user_id', 'resource_group_id', name='ehr_page_auth_unique_resource_user_team_member_ids')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ClientEHRPageAuthorizations')
    op.drop_constraint('LookupEHR_resource_group_id_fk', 'LookupClinicalCareTeamResources', type_='foreignkey')
    op.drop_column('LookupClinicalCareTeamResources', 'resource_group_id')
    op.drop_table('LookupEHRPages')

    # ### end Alembic commands ###
