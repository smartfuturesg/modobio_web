"""Create trigger for updated_at

Revision ID: 3a2f62d17c7f
Revises: 1882fcff5c14
Create Date: 2022-06-09 11:24:46.320781

"""
from alembic import op
import sqlalchemy as sa
from odyssey import db

# revision identifiers, used by Alembic.
revision = '3a2f62d17c7f'
down_revision = '1882fcff5c14'
branch_labels = None
depends_on = None

create_refresh_updated_at_func = """
    CREATE OR REPLACE FUNCTION {schema}.refresh_updated_at()
    RETURNS TRIGGER
    LANGUAGE plpgsql AS
    $func$
    BEGIN
    NEW.updated_at := now();
    RETURN NEW;
    END
    $func$;
"""

create_trigger = """
    CREATE OR REPLACE TRIGGER trig_{table}_updated BEFORE UPDATE ON {schema}."{table}"
    FOR EACH ROW EXECUTE PROCEDURE {schema}.refresh_updated_at();
    """

TABLE_LIST = db.engine.table_names()

def upgrade():
    #Add updated_at triggers for all tables
    op.execute(sa.text(create_refresh_updated_at_func.format(schema="public")))
    for table in TABLE_LIST:
        if table != 'alembic_version':
            op.execute(sa.text(create_trigger.format(schema="public", table=table)))

def downgrade():
    op.execute(sa.text("DROP FUNCTION public.refresh_updated_at() CASCADE"))