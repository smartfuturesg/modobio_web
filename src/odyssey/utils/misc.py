""" Utility functions for the odyssey package. """

import re
import statistics
import uuid

from datetime import datetime, date, time

import flask.json
from odyssey.models.client import ClientInfo, RemoteRegistration, ClientFacilities
from odyssey.models.doctor import MedicalBloodTests, MedicalBloodTestResultTypes
from odyssey.models.misc import RegisteredFacilities
from odyssey.api.errors import UserNotFound, FacilityNotFound, RelationAlreadyExists, TestNotFound, ResultTypeNotFound


_uuid_rx = re.compile(r'[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}', flags=re.IGNORECASE)

def list_average(values_list):
    """Helper function to clean list values before attempting to find the average"""
    # remove empty items
    values_list_ = [val for val in values_list if val is not None]
    if len(values_list_)>0:
        return statistics.mean(values_list_)
    else:
        return None

def check_client_existence(clientid):
    """Check that the client is in the database
    All clients must be in the CLientInfo table before any other procedure"""
    client = ClientInfo.query.filter_by(clientid=clientid).one_or_none()
    if not client:
        raise UserNotFound(clientid)

def check_blood_test_existence(testid):
    """Check that the blood test is in the database"""
    test = MedicalBloodTests.query.filter_by(testid=testid).one_or_none()
    if not test:
        raise TestNotFound(testid)

def check_blood_test_result_type_existence(result_name):
    """Check that a supplied blood test result type is in the database"""
    result = MedicalBloodTestResultTypes.query.filter_by(result_name=result_name).one_or_none()
    if not result:
        raise ResultTypeNotFound(result_name)

def check_facility_existence(facility_id):
    facility = RegisteredFacilities.query.filter_by(facility_id=facility_id).one_or_none()
    if not facility:
        raise FacilityNotFound(facility_id)

def check_client_facility_relation_existence(clientid, facility_id):
    relation = ClientFacilities.query.filter_by(client_id=clientid,facility_id=facility_id).one_or_none()
    if relation:
        raise RelationAlreadyExists(clientid, facility_id)

def check_remote_client_portal_validity(portal_id):
    """
    Ensure portal is valid. If not raise 404 error
    """
    remote_client = RemoteRegistration().check_portal_id(portal_id)

    if not remote_client:
        raise UserNotFound(message="Unauthorized. Portal is either expired or never existed")

    return remote_client

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
        if isinstance(obj, (date, datetime, time)):
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
    5. The method name must start with 'parse\\_' to be picked up by the
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
            dt = date.fromisoformat(string)
        except TypeError:
            # Not a string
            pass
        except ValueError:
            try:
                # Will fail on full datetime string
                dt = time.fromisoformat(string)
            except ValueError:
                try:
                    dt = datetime.fromisoformat(string)
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
