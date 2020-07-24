""" Utility functions for the odyssey package. """

import datetime
import re
import uuid
import flask.json



_uuid_rx = re.compile('[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}', flags=re.IGNORECASE)

class JSONEncoder(flask.json.JSONEncoder):
    """ Converts :class:`datetime.datetime`, :class:`datetime.date`,
        or :class:`datetime.time` objects to a JSON compatible ISO8601 string.

    This subclass of :class:`flask.json.JSONEncoder` overrides the
    :meth:`default` method to convert datetime objects to ISO8601 strings,
    instead of the RFC 822 strings. RFC 822 strings are much harder to
    deserialize. Everything else is passed on to the parent class.
    """
    def default(self, obj):
        """ Convert a Python object to a JSON string. """
        if isinstance(obj, (datetime.date, datetime.datetime, datetime.time)):
            return obj.isoformat()
        return super().default(obj)


class JSONDecoder(flask.json.JSONDecoder):
    """ Deserialize JSON string into a dictionary of Python objects.

    :class:`flask.json.JSONDecoder` only supports a small set of types that
    can be deserialized into Python objects. This class adds a set of parsers
    that can convert JSON strings into their respective Python objects.
    
    To add more functionality, simply create a new parser method below, with
    the following properties:

    1. The method must have 1 argument, a string.
    2. The method must return 1 object, the converted string.
    3. The method should not raise an error if the conversion fails.
    4. If the conversion was unsuccessful, the method must return the
       original string unaltered.
    5. The method name must start with 'parse\_' to be picked up by the
       automatic registration system.
    
    Of course, there should be a corresponding serializer in :class:`JSONEncoder`.
    """
    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.parse
        super().__init__(*args, **kwargs)

        self.registered_parsers = []
        # Don't use self.__dict__ here, or you'll pick up parsers from
        # parent (they're also called parse_xxx) that already have been applied
        for name, func in JSONDecoder.__dict__.items():
            if name.startswith('parse_'):
                self.registered_parsers.append(func)


    def parse_datetime(self, string: str):
        """ Convert a string to a :class:`datetime` object.

        Parameters
        ----------
        string: str
            ISO8601 formatted datetime (yyyy-mm-dd HH:MM:ss.ssssss), date (yyyy-mm-dd),
            or time (HH:MM:ss.ssssss) string. Timezone information (+/-tttt after time)
            is not yet handled.

        Returns
        -------
        :class:`datetime.datetime`, :class:`datetime.date`, or :class:`datetime.time` object, or the original string if string could not be converted.
        """
        dt = None
        try:
            # Will fail on full datetime string
            dt = datetime.date.fromisoformat(string)
        except TypeError:
            # Not a string
            pass
        except ValueError:
            try:
                # Will fail on full datetime string
                dt = datetime.time.fromisoformat(string)
            except ValueError:
                try:
                    dt = datetime.datetime.fromisoformat(string)
                except ValueError:
                    # Not a datetime string
                    pass
        if dt:
            return dt
        return string

    def parse_uuid(self, string):
        """ Convert a string into a :class:`uuid.UUID` object.

        Serializing :class:`uuid.UUID` is supported by :class:`flask.json.JSONEncoder`,
        but the reverse process is not natively supported by flask. This parser adds
        support for the deserialization of UUID strings into :class:`uuid.UUID`
        objects.

        Parameters
        ----------
        string : str
            UUID compatible string, e.g. '56128bcc-da87-3204-892e-177f8df298a8'.

        Returns
        -------
        :class:`uuid.UUID` or the original string if it could not be converted.
        """
        if _uuid_rx.match(string):
            return uuid.UUID(hex=string)
        return string

    def parse(self, jsonobj):
        """ Apply the registered parsers to the Python dict. """
        if isinstance(jsonobj, str):
            for parser in self.registered_parsers:
                obj = parser(self, jsonobj)
                if not obj is jsonobj:
                    return obj
        elif isinstance(jsonobj, (list, tuple)):
            return [self.parse(j) for j in jsonobj]
        elif isinstance(jsonobj, dict):
            for k, v in jsonobj.items():
                jsonobj[k] = self.parse(v)
        return jsonobj
