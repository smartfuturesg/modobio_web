"""empty message

Revision ID: 3fb9896eadc9
Revises: 1c0a83fb65e5
Create Date: 2022-06-03 15:15:54.588199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fb9896eadc9'
down_revision = '1c0a83fb65e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LookupEmotes',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('clock_timestamp()'), nullable=True),
    sa.Column('idx', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('icon_name', sa.String(), nullable=True),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('title_text', sa.String(), nullable=True),
    sa.Column('content_text', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('idx'),
    sa.UniqueConstraint('position')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LookupEmotes')
    # ### end Alembic commands ###
