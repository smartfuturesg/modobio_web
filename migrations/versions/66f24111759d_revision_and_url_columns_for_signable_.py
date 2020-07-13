"""revision and url columns for signable documents.

Revision ID: 66f24111759d
Revises: 41333abdd3da
Create Date: 2020-07-08 17:24:18.605944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66f24111759d'
down_revision = '41333abdd3da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ClientConsent', sa.Column('revision', sa.String(length=10), nullable=True))
    op.add_column('ClientConsent', sa.Column('url', sa.String(length=200), nullable=True))
    op.add_column('ClientConsultContract', sa.Column('revision', sa.String(length=10), nullable=True))
    op.add_column('ClientConsultContract', sa.Column('url', sa.String(length=200), nullable=True))
    op.add_column('ClientIndividualContract', sa.Column('revision', sa.String(length=10), nullable=True))
    op.add_column('ClientIndividualContract', sa.Column('url', sa.String(length=200), nullable=True))
    op.add_column('ClientPolicies', sa.Column('revision', sa.String(length=10), nullable=True))
    op.add_column('ClientPolicies', sa.Column('url', sa.String(length=200), nullable=True))
    op.add_column('ClientRelease', sa.Column('revision', sa.String(length=10), nullable=True))
    op.add_column('ClientRelease', sa.Column('url', sa.String(length=200), nullable=True))
    op.add_column('ClientSubscriptionContract', sa.Column('revision', sa.String(length=10), nullable=True))
    op.add_column('ClientSubscriptionContract', sa.Column('url', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ClientSubscriptionContract', 'url')
    op.drop_column('ClientSubscriptionContract', 'revision')
    op.drop_column('ClientRelease', 'url')
    op.drop_column('ClientRelease', 'revision')
    op.drop_column('ClientPolicies', 'url')
    op.drop_column('ClientPolicies', 'revision')
    op.drop_column('ClientIndividualContract', 'url')
    op.drop_column('ClientIndividualContract', 'revision')
    op.drop_column('ClientConsultContract', 'url')
    op.drop_column('ClientConsultContract', 'revision')
    op.drop_column('ClientConsent', 'url')
    op.drop_column('ClientConsent', 'revision')
    # ### end Alembic commands ###
