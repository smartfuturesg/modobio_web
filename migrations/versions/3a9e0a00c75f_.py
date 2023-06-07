"""empty message

Revision ID: 3a9e0a00c75f
Revises: b26e574b59f8
Create Date: 2023-06-07 17:20:01.411714

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a9e0a00c75f'
down_revision = 'b26e574b59f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Admins',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('admin_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.Column('organization_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['member_id'], ['Members.member_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['Organizations.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('admin_id'),
    sa.UniqueConstraint('member_id', 'organization_id')
    )
    op.create_table('Members',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('member_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('organization_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['Organizations.uuid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('member_id'),
    sa.UniqueConstraint('user_id', 'organization_id')
    )
    op.create_table('Organizations',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('max_members', sa.Integer(), nullable=False),
    sa.Column('max_admins', sa.Integer(), nullable=False),
    sa.Column('owner', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner'], ['Admins.admin_id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Organizations')
    op.drop_table('Members')
    op.drop_table('Admins')
    # ### end Alembic commands ###
