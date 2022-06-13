import imp
import logging
logger = logging.getLogger(__name__)

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import text
from sqlalchemy import event, DDL

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class BaseModel(db.Model):
    """
    SQLAlchemy base model used to create all other models.
    Models that are declared with this base will automatically have "created_at" and "updated_at" columns.
    They will also have a __tablename__ that is identical to their class name.
    """
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    created_at = db.Column(db.DateTime, server_default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, server_default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """


@event.listens_for(BaseModel, "instrument_class", propagate=True)
def instrument_class(mapper, class_):
    print(mapper.local_table)
    if mapper.local_table is not None:
         trigger_for_update(mapper.local_table)

def trigger_for_update(table):
    trig_ddl = DDL(f"""
            CREATE OR REPLACE TRIGGER trig_{table.name}_updated BEFORE UPDATE ON public.{table.name}
            FOR EACH ROW EXECUTE PROCEDURE public.refresh_updated_at();
            """)
    event.listen(table, 'after_create', trig_ddl)


class BaseModelWithIdx(BaseModel):
    """
    Base model for tables that use the generic index name (idx)
    Inherits the attributes from the above base model but adds in an 'idx' column
    """
    __abstract__ = True

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

class UserIdFkeyMixin:
    """
    Mixin for tables that require a foriegn key to the User.user_id column
    BE CAREFUL to only use this mixin when you intend to user Cascade deletion with this fkey
    """
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
        """
        User ID number, foreign key to User.user_id

        :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
        """

class ReporterIdFkeyMixin:
    """
    Mixin for tables that require a reporter_id (user that reported the data) foreign key
    """
    @declared_attr
    def reporter_id(cls):
        return db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
        """
        Reporter ID number, foreign key to User.user_id

        :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
        """