import logging

logger = logging.getLogger(__name__)

from flask import current_app
from flask_accepts import responds
from flask_restx import Namespace

from odyssey import db
from odyssey.utils.base.resources import BaseResource

ns = Namespace("version", description="Endpoint for API version.")


@ns.route("/")
class VersionEndpoint(BaseResource):
    @ns.doc(security=None)
    @responds(
        {"name": "version", "type": str},
        {"name": "db_version", "type": str},
        status_code=200,
        api=ns,
    )
    def get(self):
        """Returns API version in response to a GET request.

        Alembic, the database migration tool, stores a version stamp in the
        database. The stamp is not a sequential version number, but a unique
        hash (similar to git hash) that identifies the current head of the
        migration chain. The current database stamp is also returned.

        Returns
        -------
        dict
            Dict with keys "version" and "db_version".
        """
        db_version = db.session.execute(
            "select version_num from alembic_version;"
        ).scalar()

        return {
            "version": current_app.config["VERSION_STRING"],
            "db_version": db_version,
        }
