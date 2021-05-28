"""remove street, zipcode, and city from ClientInfo

Revision ID: f363b1803f0f
Revises: dfb42380a67f
Create Date: 2021-05-26 09:02:33.533165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f363b1803f0f'
down_revision = 'dfb42380a67f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ClientInfo', 'street')
    op.drop_column('ClientInfo', 'city')
    op.drop_column('ClientInfo', 'zipcode')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ClientInfo', sa.Column('zipcode', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('city', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('ClientInfo', sa.Column('street', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
