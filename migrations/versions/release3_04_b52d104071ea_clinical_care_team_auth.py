"""Clinical care team resources lookup table, care team authorizations

Revision ID: b52d104071ea
Revises: 599aa0b1eb85
Create Date: 2021-01-21 10:01:51.620554

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'b52d104071ea'
down_revision = 'bb3b600fac2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupClinicalCareTeamResources',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('resource_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('resource_name', sa.String(), nullable=True),
    sa.Column('display_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('resource_id')
    )
    op.create_table('ClientClinicalCareTeamAuthorizations',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('team_member_user_id', sa.Integer(), nullable=False),
    sa.Column('resource_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['resource_id'], ['LookupClinicalCareTeamResources.resource_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['team_member_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.create_unique_constraint('care_team_auth_unique_resource_user_team_member_ids', 
                                'ClientClinicalCareTeamAuthorizations', 
                                ['user_id', 'team_member_user_id', 'resource_id'])
                                
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ClientClinicalCareTeamAuthorizations')
    op.drop_table('LookupClinicalCareTeamResources')
    # ### end Alembic commands ###
