"""Custom converters for routes.

Flask allows the use of variables in URLs. These variables, a.k.a. path parameters, are
automatically converted to Python objects. Flask includes converters for int, float, or
path (string with backslashes). This module adds additional path parameter converters.
"""
import uuid
from datetime import date, datetime, time

import dateutil
from werkzeug.routing import BaseConverter

__all__ = [
    'UUIDConverter',
    'DateTimeConverter',
    'DateConverter',
    'TimeConverter',
]


class UUIDConverter(BaseConverter):
    """Convert path parameter into UUID."""

    name = 'uuid'

    def to_python(self, value: str) -> uuid.UUID:
        return uuid.UUID(value)

    def to_url(self, obj: uuid.UUID) -> str:
        return str(obj)


class DateTimeConverter(BaseConverter):
    """Convert path parameter into timezone-aware ISO8601 datetime.

    The :class:`datetime.datetime` will be timezone-aware only if a timezone was passed in.
    It will be a naive object otherwise.
    """

    name = 'datetime'

    def to_python(self, value: str) -> datetime:
        return dateutil.parser.isoparse(value)

    def to_url(self, obj: datetime) -> str:
        return obj.isoformat()


class DateConverter(BaseConverter):
    """Convert path parameter into ISO8601 date.

    :class:`datetime.date` objects are never timezone-aware.
    """

    name = 'date'

    def to_python(self, value: str) -> date:
        return date.fromisoformat(value)

    def to_url(self, obj: date) -> str:
        return obj.isoformat()


class TimeConverter(BaseConverter):
    """Convert path parameter into timezone-aware ISO8601 timestamp.

    The :class:`datetime.time` will be timezone-aware only if a timezone was passed in.
    It will be a naive object otherwise.
    """

    name = 'time'

    def to_python(self, value: str) -> time:
        d = dateutil.parser.parse(value)
        return d.time().replace(tz=d.tzinfo)

    def to_url(self, obj: time) -> str:
        return obj.isoformat()
