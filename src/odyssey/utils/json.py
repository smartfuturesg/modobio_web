import dataclasses
import json
import uuid
from datetime import date, datetime, time

import dateutil
import flask.json.provider
import pytz


def remove_timezone_from_timestamps(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.replace(tzinfo=None)
            else:
                remove_timezone_from_timestamps(value)
    elif isinstance(data, list):
        for item in data:
            remove_timezone_from_timestamps(item)


class JSONEncoder(json.JSONEncoder):
    """Serialize a Python object into a JSON string.

    :class:`json.JSONEncoder` only supports a small set of types that can be serialized into
    JSON strings. This class adds extends the default serializer to stringify more objects.

    To add more serializers, extend the :meth:`default` method.

    Create a corresponding deserializer in :class:`JSONDecoder`.
    """
    def default(self, obj, **kwargs):
        """Serialize Python objects into a JSON string.

        Parameters
        ----------
        obj : object
            Any Python object that needs to be converted to a string.

        Returns
        -------
        str
            JSON representation of the Python object.
        """
        if isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        return super().default(obj, **kwargs)


class JSONDecoder(json.JSONDecoder):
    """Deserialize a JSON string into a dictionary of Python objects.

    :class:`json.JSONDecoder` only supports a small set of types that can be deserialized into
    Python objects. This class adds extra parsers that can convert JSON strings into their
    Python objects.

    New behaviour:

    - Keys are interpreted as well as values.
    - Now {"a":"2000"} is interpreted as a number, not left as a string.
    - UUIDs are interpreted as uuid.UUID objects.
    - Dates and times are interpreted as date, time, or datetime objects.

    To add another parser, create a new method with the following properties:

    1.  The method must have 1 argument, a string.
    2.  The method must return 1 object, the converted object or the original string if it could
        not be converted.
    3.  The method should not raise an error if the conversion fails. Instead, the original
        string should be returned.

    Add the method to ``PARSERS`` in the ``__init__`` method. Take care of the place in that list,
    the parsers are executed in order.

    Create a corresponding serializer in :class:`JSONEncoder` if needed.
    """
    def __init__(self, *args, **kwargs):
        kwargs['object_pairs_hook'] = self._parse
        super().__init__(*args, **kwargs)

        # Removed auto-registration in favour of fixed list
        # to control order in which parsers are applied.
        self.PARSERS = (
            self.parse_number,
            self.parse_uuid,
            self.parse_datetime,
        )

    def _parse(self, jsonobjs: list) -> dict:
        """Apply the registered parsers to a list of key, value pairs."""
        ret = {}
        for key, val in jsonobjs:
            if isinstance(key, str):
                for parser in self.PARSERS:
                    key = parser(key)
            if isinstance(val, str):
                for parser in self.PARSERS:
                    val = parser(val)
            ret[key] = val
        return ret

    def parse_number(self, string: str):
        """Convert a string into a number.

        For JSON string '{"a": 2000, "b": "2000"}', the standard Python json module interprets
        "a" as a number and "b" as a string. "b" does not get converted to a number. This parser
        remedies that situation.

        Parameters
        ----------
        string : str
            The JSON string containing a number.

        Returns
        -------
        int or float
            The number interpreted as a :func:`int` or :func:`float`, or ``string`` if the
            conversion failed.
        """
        try:
            return self.parse_int(string)
        except TypeError:
            # Not a string
            return string
        except ValueError:
            try:
                return self.parse_float(string)
            except ValueError:
                # Add more types here: Decimal?
                # float converts numbers outside of range to inf
                # and doesn't raise error. Needs extra checks.
                return string

    def parse_datetime(self, string: str):
        """Convert a string to a :mod:`datetime` object.

        If the string contains just a date in ISO format (yyyy-mm-dd), a :class:`datetime.date`
        object is returned. If the string contains just a time in ISO format (HH:MM:SS.SSSSSS),
        a :class:`datetime.time` object is returned. If the string contains a full date and time,
        or anything that is not strict ISO format but can be interpreted by DateUtil parser
        :func:`dateutil.parser.parse`, a :class:`datetime.datetime` object is returned.

        Strings that contain only a single number (convertable by int or float) are **not**
        passed to dateutil. Dateutil interprets a single integer as a year with some default
        month and day. Those cases are left as string.

        Parameters
        ----------
        string : str
            String containing date and/or time.

        Returns
        -------
        :mod:`datetime`
            Classes of :mod:`datetime` depending on the input string, or the original string if it
            could not be parsed into a datetime object.
        """
        # dateutil interprets "2000" as an incomplete date. Filter out numbers first.
        try:
            int(string)
        except TypeError:
            # Not a string
            return string
        except ValueError:
            pass
        else:
            # Just an integer, keep string.
            return string

        try:
            float(string)
        except ValueError:
            pass
        else:
            # Just a number, keep string.
            return string

        # Just date
        try:
            return date.fromisoformat(string)
        except ValueError:
            pass

        # Just time
        try:
            return time.fromisoformat(string)
        except ValueError:
            pass

        # Full datetime, maybe with timezone.
        try:
            return dateutil.parser.parse(string)
        except dateutil.parser.ParserError:
            pass

        # Some timestamps from Terra have an H:M:S format for timezone offset
        # e.g. 2023-03-19T00:39:35-07:00:00
        # Datetime allows for seconds in the timezone offset, but dateutil does not.
        try:
            return datetime.fromisoformat(string)
        except ValueError:
            # Not a datetime string
            return string

    def parse_uuid(self, string: str):
        """Convert a string into a :class:`uuid.UUID` object.

        Parameters
        ----------
        string : str
            UUID compatible string, e.g. '56128bcc-da87-3204-892e-177f8df298a8'.

        Returns
        -------
        :class:`uuid.UUID`
             The original string is returned if it could not be converted to a UUID.
        """
        try:
            return uuid.UUID(hex=string)
        except (ValueError, TypeError, AttributeError):
            return string


class JSONProvider(flask.json.provider.JSONProvider):
    """Extends JSONProvider with better datetime and uuid (de)serialization."""
    def __init__(self, app=None, **kwargs):
        if app:
            super().__init__(app=app, **kwargs)

    @staticmethod
    def process_terra_data(data):
        if 'data' in data:
            for item in data['data']:
                if (
                    'metadata' in item and 'start_time' in item['metadata']
                    and isinstance(item['metadata']['start_time'], datetime)
                ):
                    start_time = item['metadata']['start_time']

                    # COROS does not have utc offset in start_time
                    # So we need to check if there is that data, or not
                    if start_time.tzinfo and start_time.tzinfo.utcoffset:
                        tz_offset_seconds = start_time.tzinfo.utcoffset(start_time).total_seconds()
                        item['metadata']['tz_offset'] = tz_offset_seconds
                        # Remove timezone from all "timestamp" fields
                        remove_timezone_from_timestamps(item)
                    else:
                        item['metadata']['tz_offset'] = None
                        # Probably don't need to remove timezone from timestamps here

        return data

    def dumps(self, obj, **kwargs) -> str:
        """Serialize data to a JSON string.

        Parameters
        ----------
        obj : object
            The data to serialize.

        kwargs : dict
            May be passed to the underlying JSON library.

        Returns
        -------
        str
            JSON formatted string.
        """
        kwargs['cls'] = JSONEncoder
        return json.dumps(obj, **kwargs)

    def loads(self, s: str, **kwargs):
        """Deserialize JSON as Python native data.

        Parameters
        ----------
        s : str
            JSON formatted string

        kwargs : dict
            May be passed to the underlying JSON library.

        Returns
        -------
        dict
            A Python dict containing the converted data.
        """
        kwargs['cls'] = JSONDecoder

        data = json.loads(s, **kwargs)

        # Process the data after deserialization
        processed_data = JSONProvider.process_terra_data(data)

        return processed_data
