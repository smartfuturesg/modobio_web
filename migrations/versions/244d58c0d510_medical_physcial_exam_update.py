"""medical physcial exam update
adds timestamp and height in inches fields. 
With this, we will deprecate the original vital height string in favor of logging
height measurements in inches (float)

Revision ID: 244d58c0d510
Revises: bdc2108da9b8
Create Date: 2020-07-31 10:54:51.339005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '244d58c0d510'
down_revision = 'bdc2108da9b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('MedicalPhysicalExam', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.add_column('MedicalPhysicalExam', sa.Column('vital_height_inches', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('MedicalPhysicalExam', 'vital_height_inches')
    op.drop_column('MedicalPhysicalExam', 'timestamp')
    # ### end Alembic commands ###
