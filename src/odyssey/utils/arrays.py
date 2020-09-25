# Array manipulation

from sqlalchemy.dialects.postgres import ARRAY


class Array(ARRAY):
    """ Postgres ARRAY type with extra functionality. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def append(self, arr: list):
        pass
