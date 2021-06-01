"""added status field to clinical care team

Revision ID: 5fb1aae9de2f
Revises: e024249f8efe
Create Date: 2021-06-01 01:44:50.681160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fb1aae9de2f'
down_revision = 'e024249f8efe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ClientClinicalCareTeamAuthorizations', sa.Column('status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ClientClinicalCareTeamAuthorizations', 'status')
    # ### end Alembic commands ###
