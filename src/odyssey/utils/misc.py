""" Utility functions for the odyssey package. """
import logging
logger = logging.getLogger(__name__)

import ast
import boto3
import inspect
import jwt
import mimetypes
import os
import random
import re
import statistics
import textwrap
import typing as t
import uuid

import pprint

from datetime import datetime, date, time
from io import BytesIO

from flask import current_app, request
import flask.json
from PIL import Image
from sqlalchemy import select
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant, VideoGrant
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import (
    BadRequest,
    RequestEntityTooLarge,
    Unauthorized,
    UnsupportedMediaType)

from odyssey import db
from odyssey.api.client.models import ClientFacilities
from odyssey.api.doctor.models import (
    MedicalBloodTests,
    MedicalBloodTestResultTypes,
    MedicalConditions,
    MedicalLookUpSTD)
from odyssey.api.facility.models import RegisteredFacilities
from odyssey.api.lookup.models import LookupDrinks
from odyssey.api.telehealth.models import TelehealthChatRooms
from odyssey.api.user.models import User, UserTokenHistory
from odyssey.utils.constants import ALLOWED_IMAGE_TYPES, ALPHANUMERIC, TWILIO_ACCESS_KEY_TTL

_uuid_rx = re.compile(r'[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}', flags=re.IGNORECASE)

def list_average(values_list):
    """Helper function to clean list values before attempting to find the average"""
    # remove empty items
    values_list_ = [val for val in values_list if val is not None]
    if len(values_list_)>0:
        return statistics.mean(values_list_)
    else:
        return None

def check_client_existence(user_id):
    """Check that the client is in the database
    All clients must be in the CLientInfo table before any other procedure"""
    client = User.query.filter_by(user_id=user_id, is_client=True, deleted=False).one_or_none()
    if not client:
        raise Unauthorized
    return client

def check_staff_existence(user_id):
    """Check that the user is in the database and is a staff member"""
    staff = User.query.filter_by(user_id=user_id, is_staff=True, deleted=False).one_or_none()
    if not staff:
        raise Unauthorized
    return staff

def check_user_existence(user_id, user_type=None):
    """Check that the user is in the database
    If user_type is 'client', check if user_id exists in ClientInfo table.
    If user_type is 'staff', check if user_id exists in StaffProfile table.
    If user_type is neither of the above, just check if user_id exists in User table.
    """
    if user_type == 'client':
        user = User.query.filter_by(user_id=user_id, is_client=True, deleted=False).one_or_none()
    elif user_type == 'staff':
        user = User.query.filter_by(user_id=user_id, is_staff=True, deleted=False).one_or_none()
    else:
        user = User.query.filter_by(user_id=user_id, deleted=False).one_or_none()
    if not user:
        raise Unauthorized
    return user

def check_blood_test_existence(test_id):
    """Check that the blood test is in the database"""
    test = MedicalBloodTests.query.filter_by(test_id=test_id).one_or_none()
    if not test:
        raise BadRequest(f'Blood test {test_id} not found.')

def check_blood_test_result_type_existence(result_name):
    """Check that a supplied blood test result type is in the database"""
    result = MedicalBloodTestResultTypes.query.filter_by(result_name=result_name).one_or_none()
    if not result:
        raise BadRequest(f'Blood test result {result_name} not found.')

def fetch_facility_existence(facility_id):
    facility = RegisteredFacilities.query.filter_by(facility_id=facility_id).one_or_none()
    if not facility:
        raise BadRequest(f'Facility {facility_id} not found.')
    return facility

def check_client_facility_relation_existence(user_id, facility_id):
    relation = ClientFacilities.query.filter_by(user_id=user_id,facility_id=facility_id).one_or_none()
    if relation:
        raise BadRequest(f'Client already associated with facility {facility_id}.')

def check_medical_condition_existence(medcon_id):
    medcon = MedicalConditions.query.filter_by(medical_condition_id=medcon_id).one_or_none()
    if not medcon:
        raise BadRequest(f'Medical condition {medcon_id} not found.')

def check_drink_existence(drink_id):
    drink = LookupDrinks.query.filter_by(drink_id=drink_id).one_or_none()
    if not drink:
        raise BadRequest(f'Drink {drink_id} not found.')
        
def check_std_existence(std_id):
    std = MedicalLookUpSTD.query.filter_by(std_id=std_id).one_or_none()
    if not std:
        raise BadRequest(f'STD {std_id} not found.')

def grab_twilio_credentials():
    """
    Helper funtion to bring up twilio credentials for API acces.
    Raises an error if one or more of the credentials are None
    """
    twilio_account_sid = current_app.config['TWILIO_ACCOUNT_SID']
    twilio_api_key_sid = current_app.config['TWILIO_API_KEY_SID']
    twilio_api_key_secret = current_app.config['TWILIO_API_KEY_SECRET']

    if any(x is None for x in [twilio_account_sid,twilio_api_key_sid,twilio_api_key_secret]):
        raise BadRequest('Twilio API credentials not found.')

    return {'account_sid':twilio_account_sid,
            'api_key': twilio_api_key_sid,
            'api_key_secret': twilio_api_key_secret}

def generate_meeting_room_name(meeting_type = 'TELEHEALTH'):
    """ Generates unique, internally used names for meeting rooms.

    Parameters
    ----------
    meeting_type : str
        Meeting types will be either TELEHEALTH or CHATROOM
    """
    _hash = "".join([random.choice(ALPHANUMERIC) for i in range(15)])

    return (meeting_type+'_'+_hash).upper()

def create_conversation(staff_user_id, client_user_id, booking_id):
    """
    Provision a Twilio conversation between the staff and client users
    """
    new_chat_room = TelehealthChatRooms(
        staff_user_id=staff_user_id,
        client_user_id=client_user_id,
        booking_id = booking_id)

    # skip twilio in testing
    if current_app.config['TESTING']:
        db.session.add(new_chat_room)
        return None
    # bring up twilio client
    twilio_credentials = grab_twilio_credentials()
    client = Client(twilio_credentials['api_key'], 
                    twilio_credentials['api_key_secret'],
                    twilio_credentials['account_sid'])

    room_name = generate_meeting_room_name(meeting_type='CHATROOM')
    # create conversation through twilio api, add participants by modobio_id
    # TODO catch possible errors from calling Twilio
    conversation = client.conversations.conversations.create(
        friendly_name=room_name
    )

    users = db.session.execute(
        select(User.modobio_id).
        where(User.user_id.in_([staff_user_id, client_user_id]))
    ).scalars().all()

    for modobio_id in users:
        conversation.participants.create(identity=modobio_id)

    # create chatroom entry into DB
    new_chat_room.conversation_sid = conversation.sid
    db.session.add(new_chat_room)

    return conversation.sid
    

def get_chatroom(staff_user_id, client_user_id, participant_modobio_id, create_new=False):
    """
    Deprecated 4.15.21
    
    Retrieves twilio chat room by searcing db for the user ids provided.
    If none exist creates a new room with provided.
    """
    # bring up twilio client
    twilio_credentials = grab_twilio_credentials()
    client = Client(twilio_credentials['api_key'], 
                    twilio_credentials['api_key_secret'],
                    twilio_credentials['account_sid'])

    # bring up the FIRST chat room, this is a small patch until we fully deprecate this function on the front end
    # if a chat between the client and staff users 
    # does not exist, create a new chat room

    chat_room = db.session.execute(
        select(TelehealthChatRooms
        ).where(
            TelehealthChatRooms.staff_user_id == staff_user_id,
            TelehealthChatRooms.client_user_id == client_user_id
        )).first()
    
    if chat_room:
        # pull down the conversation from Twilio, add user
        room_name = chat_room[0].room_name
        conversation = client.conversations.conversations(chat_room[0].conversation_sid).fetch()
    elif create_new:
        # if no chat room exists yet, create a new one
        room_name = generate_meeting_room_name(meeting_type='CHATROOM')

        conversation = client.conversations.conversations.create(
            friendly_name=room_name)

        # create chatroom entry into DB
        new_chat_room = TelehealthChatRooms(
            staff_user_id=staff_user_id,
            client_user_id=client_user_id,
            room_name = room_name,
            conversation_sid = conversation.sid)
        db.session.add(new_chat_room)
    else:
        # no chat room exists and a new one will not be created
        raise BadRequest('Chat room does not exist.')
    # Add participant to chat room using their modobio_id
    try:
        conversation.participants.create(identity=participant_modobio_id)
    except TwilioRestException as exc:
        # do not error if the user is already in the conversation
        if exc.status != 409:
            raise
    
    db.session.commit()
    return conversation

def create_twilio_access_token(modobio_id, meeting_room_name=None):
    """
    Generate a twilio access token for the provided modobio_id
    """
    if current_app.config['TESTING']:
        return

    twilio_credentials = grab_twilio_credentials()
    token = AccessToken(twilio_credentials['account_sid'],
                    twilio_credentials['api_key'],
                    twilio_credentials['api_key_secret'],
                    identity=modobio_id,
                    ttl=TWILIO_ACCESS_KEY_TTL)

    token.add_grant(ChatGrant(service_sid=current_app.config['CONVERSATION_SERVICE_SID']))
    if meeting_room_name:
        token.add_grant(VideoGrant(room=meeting_room_name))

    return token.to_jwt()

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


def verify_jwt(token, error_message="", refresh=False):
    """
    Ensure token is signed correctly and is not yet expired
    Returns the token's payload
    """
    secret = current_app.config['SECRET_KEY']
    try:
        decoded_token = jwt.decode(token, secret, algorithms='HS256')
    except:
        # log the refresh attempt
        if refresh:
            token_payload = jwt.decode(token, options={'verify_signature': False})
            db.session.add(UserTokenHistory(user_id=token_payload.get('uid'), 
                                        event='refresh',
                                        ua_string = request.headers.get('User-Agent')))
            db.session.commit()
            
        raise Unauthorized(error_message)

    return decoded_token


class FileHandling:
    """ A class for handling files. """

    def __init__(self):
        """ Initiate the ImageHandling class instance

        Loads the AWS s3 bucket service as part of initialization process.
        """
        self.s3_resource = boto3.resource('s3')
        self.s3_bucket_name = current_app.config['AWS_S3_BUCKET']
        self.s3_prefix = current_app.config['AWS_S3_PREFIX']
        if self.s3_prefix and not self.s3_prefix.endswith('/'):
            self.s3_prefix += '/'
        self.s3_bucket = self.s3_resource.Bucket(self.s3_bucket_name)
        mimetypes.add_type('audio/mp4', '.m4a')

    def validate_file_type(self, file: FileStorage, allowed_file_types: tuple) -> str:
        # validate the file is allowed
        file_extension = mimetypes.guess_extension(file.mimetype)
        if file_extension not in allowed_file_types:
            raise UnsupportedMediaType(
                f'File {file.name} not allowed. Allowed types are {allowed_file_types}.')

        return file_extension

    def validate_file_size(self, file: FileStorage, max_file_size):
        # validate file size is below max_file_size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        if file_size > max_file_size:
            raise RequestEntityTooLarge(f'File {file.name} exceeds maximum file size.')

    def image_crop_square(self, file: FileStorage) -> FileStorage:
        # validate_file_type(...) is an image
        img_type = self.validate_file_type(file, ALLOWED_IMAGE_TYPES)
        # crop into square
        img = Image.open(file)
        img_w, img_h = img.size

        squared_img = img
        # if image isn't a square, 
        # find the shortest side and crop to a square with length=shortest_side.
        if img_w != img_h:
            crop_len= ( max(img_w,img_h) - min(img_w,img_h) ) // 2
            extra = max(img_w, img_h) % 2 # 0 if largest is even, 1 if largest is odd
            if img_w > img_h:
                (left,upper,right,lower)=(crop_len, 0, img_w - crop_len - extra, img_h)
            else:
                (left,upper,right,lower)=(0, crop_len, img_w, img_h - crop_len - extra)
            squared_img = img.crop((left,upper,right,lower))
        # return image in a FileStorage object
        temp = BytesIO()
        default_format = 'jpeg'
        # convert image to rgb so we can save pngs to jpegs
        if img_type.lower() == ".png":
            squared_img = squared_img.convert('RGB')
        squared_img.save(temp, format=default_format, quality=90)
        res = FileStorage(temp, filename=f'squared.{default_format}', content_type=f'image/{default_format}')

        return res

    def image_resize(self, file: FileStorage, dimensions: tuple) -> Image:
        # validate_file_type(...)  is an image
        img_type = self.validate_file_type(file, ALLOWED_IMAGE_TYPES)
        # Resize image
        img = Image.open(file)
        # dimensions tuple (w, h)
        img_w, img_h = dimensions
        resized = img.copy()
        resized.thumbnail((img_w, img_h))
        # return image in a FileStorage object
        temp = BytesIO()
        default_format = 'jpeg'
        # convert image to rgb so we can save pngs to jpegs
        if img_type.lower() == ".png":
            resized = resized.convert('RGB')
        resized.save(temp, format=default_format , quality=90)
        res = FileStorage(temp, filename=f'size{img_w}x{img_h}.{default_format}', content_type=f'image/{default_format}')
        
        return res
    
    def save_file_to_s3(self, file: FileStorage, filename: str):
        # Just saves, nothing returned
        file.seek(0)
        self.s3_bucket.put_object(Key=self.s3_prefix + filename, Body=file.stream)

    def get_presigned_urls(self, prefix: str) -> dict:
        # returns all files found with defined prefix
        # dictionary is {filename1: url1, filename2: url2...}
        res = {}
        params = {'Bucket': self.s3_bucket_name}
        for file in self.s3_bucket.objects.filter(Prefix=self.s3_prefix + prefix):
            params['Key'] = file.key
            url = self.s3_resource.meta.client.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
            file_name = file.key.split('/')[-1]
            res[file_name] = url
        return res
    
    def get_presigned_url(self, file_path: str) -> str:
        # returns a single url with defined file_path
        # if file_path doesn't exists in S3, it will return an empty string
        params = {'Bucket': self.s3_bucket_name}
        url = ''
        for file in self.s3_bucket.objects.filter(Prefix=self.s3_prefix + file_path):
            params['Key'] = file.key
            url = self.s3_resource.meta.client.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
        return url

    def delete_from_s3(self, prefix):
        self.s3_bucket.objects.filter(Prefix=self.s3_prefix + prefix).delete()


class DecoratorVisitor(ast.NodeVisitor):
    """ Find decorators placed on functions or classes. """
    decorators = []

    def visit_FunctionDef(self, node):
        """ For a node that is a :class:`ast.FunctionDef`, collect its decorators. """
        self.decorators.extend(node.decorator_list)

    def visit_ClassDef(self, node):
        """ For a node that is a :class:`ast.ClassDef`, collect its decorators. """
        self.decorators.extend(node.decorator_list)


def find_decorator_value(
        function: t.Callable,
        decorator: str,
        argument: int=None,
        keyword: str=None
    ) -> t.Any:
    """ Return the value of an argument or keyword passed to a decorator placed on a function or class.

    For example, in the code ::

        class SomeEndpoint(BaseResource):
            @accepts(schema=SomeSchema)
            def post(self):
                ...

        schema = find_decorator_value(SomeEndpoint.post, decorator='accepts', keyword='schema')

    :func:`find_decorator_value` will find the decorator :func:`@accepts` which is decorating
    :func:`post()` and return the value ``SomeSchema`` passed to the argument :attr:`schema`.

    This function can also find positional arguments passed into the decorator::

        class SomeEndpoint(BaseResource):
            # incorrect use of @accepts for this example only
            @accepts('x', 3, SomeSchema)
            def post(self):
                ...

        schema = find_decorator_value(SomeEndpoint.post, decorator='accepts', argument=2)

    will return the same ``SomeSchema`` object as the first example.

    Params
    ------
    function : Callable
        A function, method, or class which has a decorator on it.

    decorator : str
        The name of the decorator to search for.

    argument : int
        The index of the positional argument passed into the decorator. Mutually exclusive
        with the ``keyword`` argument, must provide exactly one.

    keyword : str
        The name of the keyword argument passed into the decorator. Mutually exclusive
        with the ``argument`` argument, must provide exactly one.

    Returns
    -------
    Any
        The value of the parameter as passed into the decorator. Can be any Python object.

    Raises
    ------
    ValueError
        Raised when called with incorrect arguments.

    TypeError
        Raised when :attr:`decorator` is not found or when :attr:`argument` or :attr:`keyword`
        are not found in the decorator.
    """
    # Check parameters
    if (keyword is None and argument is None) or (keyword is not None and argument is not None):
        raise ValueError('You must provide exactly one of "keyword" or "argument".')

    if argument is not None and not isinstance(argument, int):
        raise ValueError('Parameter "argument" must be integer.')

    if keyword is not None and not isinstance(keyword, str):
        raise ValueError('Parameter "keyword" must be string.')

    if decorator.startswith('@'):
        decorator = decorator[1:]

    # Get actual function, not the one wrapped by a decorator
    top_func = inspect.unwrap(function)

    # Get source code of function/class definition, convert to AST representation.
    extralines = []
    if inspect.isclass(top_func):
        # inspect.getsource(classobj) does NOT include decorators, unlike functions and methods.
        # Get previous lines if any of them include '@'
        wholefile, lineno = inspect.findsource(top_func.__class__)
        lineno -= 1
        while lineno >= 0:
            line = wholefile[lineno].strip()
            if line.startswith('@'):
                extralines.append(wholefile[lineno])
                lineno -= 1
                continue

            # It is legal to intersperse decorators with empty lines and comments.
            # Keep searching in that case.
            if (not line or line.startswith('#')):
                lineno -= 1
                continue

            break

    code = inspect.getsource(top_func)
    code = '\n'.join(extralines) + code
    code = textwrap.dedent(code)
    tree = ast.parse(code)

    # Find decorators
    visitor = DecoratorVisitor()
    visitor.visit(tree)

    # Decorators can be called in 4 different ways.
    # Each way is represented differently in AST.
    #
    # 1. @aaa               Name(id='aaa')
    # 2. @aaa(1, kw=2)      Call(func=Name(id='aaa'),
    #                           args=[Constant(value=1)],
    #                           keywords=[keyword(arg='kw', value=Constant(value=2))])
    # 3. @AAA.aaa           Attribute(value=Name(id='AAA'), attr='aaa')
    # 4. @AAA.aaa(1, kw=2)  Call(func=Attribute(value=Name(id='AAA'), attr='aaa'),
    #                           args=[Constant(value=3)],
    #                           keywords=[keyword(arg='kw', value=Constant(value=2)))

    # Map decorator names to AST nodes
    decos = {}
    for deco in visitor.decorators:
        if isinstance(deco, ast.Name):
            deco_name = deco.id
        elif isinstance(deco, ast.Attribute):
            deco_name = deco.value.id + '.' + deco.attr
        elif isinstance(deco, ast.Call):
            if isinstance(deco.func, ast.Name):
                deco_name = deco.func.id
            elif isinstance(deco.func, ast.Attribute):
                deco_name = deco.func.value.id + '.' + deco.func.attr
            else:
                raise TypeError(f'Unknown decorator Call type found {deco}.')
        else:
            raise TypeError(f'Unknown decorator type found {deco}.')

        decos[deco_name] = deco

    if decorator not in decos:
        raise TypeError(f'Decorator {decorator} not found on {function}.')

    # Continue with the requested decorator
    deco = decos[decorator]

    # Find the AST node that represents either the argument or the keyword value.
    value = None
    if argument is not None:
        if not hasattr(deco, 'args'):
            raise TypeError(f'Decorator @{deco_name} has no positional arguments.')

        try:
            value = deco.args[argument]
        except IndexError:
            argno = len(deco.args)
            raise TypeError(f'Decorator @{deco_name} has only {argno} argument(s).')
    else:
        if not hasattr(deco, 'keywords'):
            raise TypeError(f'Decorator @{deco_name} has no keyword arguments.')

        kws = {kw.arg: kw.value for kw in deco.keywords}
        if keyword not in kws:
            raise TypeError(f'Keyword {keyword} not found in decorator @{deco_name}.')

        value = kws[keyword]

    # Get actual object from AST node; this is where it gets really hard.
    #
    # At this point we have an AST representation of the value passed in to the
    # decorator, either by argument or by keyword. We want the actual object of
    # that value, not just the AST representation. I don't know how to get that.
    #
    # I tried to analyze the frame stack (inspect.stack()). Calling frames hold
    # references to objects in memory. However, the stack is linear going from
    # the main caller (__main__ or thread start or something similar) to the
    # current frame. Another decorator that was called and finshed is no longer
    # on the stack.
    #
    # For now this will return only a few simple cases. It will not raise an
    # error for missing cases as there are too many, simply return None.

    if isinstance(value, ast.Constant):
        # int, str, or None
        return value.value
    elif isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        # Only support collections of Constant, nothing nested or more complicated.
        if not all([isinstance(elt, ast.Constant) for elt in value.elts]):
            return

        elts = [elt.value for elt in value.elts]
        if isinstance(value, ast.List):
            return elts
        elif isinstance(value, ast.Tuple):
            return tuple(elts)
        else:
            return set(elts)
    elif isinstance(value, ast.Dict):
        # Only support simple dicts where both keys and values are Constant.
        if not all([isinstance(elt, ast.Constant) for elt in value.keys + value.values]):
            return

        return {k.value: v.value for k, v in zip(value.keys, value.values)}
    elif isinstance(value, ast.Name):
        # Value is a variable name, which means it must be defined or imported.
        # See if it's defined in the globals section of the function/class
        # on which the decorator was placed.
        # TODO: widen search, maybe go up the tree to search in globals for nested
        # function/class definitions, all the way up to module.
        if value.id in top_func.__globals__:
            return top_func.__globals__[value.id]
