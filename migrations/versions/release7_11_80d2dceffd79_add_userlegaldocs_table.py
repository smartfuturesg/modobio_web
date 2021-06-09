"""add UserLegalDocs table

Revision ID: 80d2dceffd79
Revises: e024249f8efe
Create Date: 2021-06-08 10:35:06.284531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80d2dceffd79'
down_revision = 'e024249f8efe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserLegalDocs',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('doc_id', sa.Integer(), nullable=True),
    sa.Column('signed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['doc_id'], ['LookupLegalDocs.idx'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('idx')
    )
    op.add_column('LookupLegalDocs', sa.Column('version', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('LookupLegalDocs', 'version')
    op.drop_table('UserLegalDocs')
    # ### end Alembic commands ###
