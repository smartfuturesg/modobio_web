"""fix table names and user biological_sex typo

Revision ID: 40e57e2da26a
Revises: a183f99bc243
Create Date: 2020-12-03 12:20:16.095048

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '40e57e2da26a'
down_revision = 'a183f99bc243'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MedicalExternalMR',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('med_record_id', sa.String(), nullable=False),
    sa.Column('institute_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['institute_id'], ['MedicalInstitutions.institute_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx'),
    sa.UniqueConstraint('user_id', 'med_record_id', 'institute_id')
    )
    op.create_table('MedicalSurgeries',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('surgery_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('client_user_id', sa.Integer(), nullable=False),
    sa.Column('reporter_user_id', sa.Integer(), nullable=False),
    sa.Column('surgery_category', sa.String(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('surgeon', sa.String(), nullable=True),
    sa.Column('institution', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporter_user_id'], ['User.user_id'], ),
    sa.PrimaryKeyConstraint('surgery_id')
    )
    op.create_table('StaffRecentClients',
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('staff_user_id', sa.Integer(), nullable=False),
    sa.Column('client_user_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['staff_user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.drop_table('ClientSurgeries')
    op.drop_table('staff_recent_clients')
    op.drop_table('ClientExternalMR')
    op.add_column('User', sa.Column('biological_sex_male', sa.Boolean(), nullable=True))
    op.drop_column('User', 'biologoical_sex_male')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('biologoical_sex_male', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('User', 'biological_sex_male')
    op.create_table('ClientExternalMR',
    sa.Column('idx', sa.INTEGER(), server_default=sa.text('nextval(\'"ClientExternalMR_idx_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('med_record_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('institute_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['institute_id'], ['MedicalInstitutions.institute_id'], name='ClientExternalMR_institute_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], name='ClientExternalMR_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='ClientExternalMR_pkey'),
    sa.UniqueConstraint('user_id', 'med_record_id', 'institute_id', name='ClientExternalMR_user_id_med_record_id_institute_id_key')
    )
    op.create_table('staff_recent_clients',
    sa.Column('idx', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('staff_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('client_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], name='staff_recent_clients_client_user_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['staff_user_id'], ['User.user_id'], name='staff_recent_clients_staff_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx', name='staff_recent_clients_pkey')
    )
    op.create_table('ClientSurgeries',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('surgery_id', sa.INTEGER(), server_default=sa.text('nextval(\'"ClientSurgeries_surgery_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('client_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('reporter_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('surgery_category', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('date', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('surgeon', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('institution', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['client_user_id'], ['User.user_id'], name='ClientSurgeries_client_user_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporter_user_id'], ['User.user_id'], name='ClientSurgeries_reporter_user_id_fkey'),
    sa.PrimaryKeyConstraint('surgery_id', name='ClientSurgeries_pkey')
    )
    op.drop_table('StaffRecentClients')
    op.drop_table('MedicalSurgeries')
    op.drop_table('MedicalExternalMR')
    # ### end Alembic commands ###
