"""
This module handles various aspects of file storage such as validation, storing
to, and retrieving from AWS S3.

Overview
--------

:class:`FileDownload` deals with files already uploaded to S3. The methods in
:class:`FileDownload` require a **full path** (or key) to the uploaded file.

.. code:: python

    # The path to the file, typically retrieved from the database.
    path = 'id00017/images/picture.jpg'
    user_id = 17

    # User_id is needed at instantiation time. Methods of this class check
    # wether the requested file is within the same prefix, which includes
    # user_id number.
    fd = FileDownload(user_id)

    # Create a "pre-signed" URL to allow frontend to download the file.
    # URL expires after some time (default 10 min).
    url = fd.url(path)

    # Delete file
    fd.delete(path)

:class:`FileUpload` deals with files not yet uploaded to S3. In contrast to
:class:`FileDownload`, the methods in :class:`FileUpload` need a **filename
only** and a full path will be created from a prefix and the supplied filename.
Read the sections below to learn more about files and prefixes.

.. code:: python

    # The data for the upload can come from anything that supports read(),
    # seek(), and tell(). That can be the handle to an opened file, a BytesIO
    # object, or the stream attribute to a FileStorage instance.
    f = response.files['file']

    # Use ImageUpload or AudioUpload for specific files.
    fu = FileUpload(f.stream, user_id, prefix='user_files')

    # Validate size and type, raises BadRequest
    fu.validate()

    # File type and extension is guessed from binary data stream.
    filename = f'filename.{fu.extension}'

    # Optionally, an additional prefix given here.
    fu.save(filename)

    # Full path available, store in db
    print(fu.filename)
    # 'id00017/user_files/filename.ext'

For uploading images or audio recordings, use :class:`ImageUpload` and
:class:`AudioUpload`, respectively. These classes guess type and validate for
the specific purpose. :class:`ImageUpload` also has a method to
:meth:`~ImageUpload.resize` the image.

Files on S3
-----------

S3's top level division is the bucket. Buckets contain objects. Each object has
a unique key. Keys may contain ``/`` characters, which make keys look like a
directory structure. In fact, in the AWS S3 console objects are displayed as
files and directories, but under the hood objects act differently.

There is no way to distinguish an object with key "path/file" from "path/file/"
(other than the name itself). There is no is_file() method or something
similar. That is because, in fact, both are *objects* and not a file or a
directory. Both objects can exist at the same time.

Another surprising fact is that empty directories are automatically deleted. So
if a file is uploaded with key "files/images/image1.jpg" and image1.jpg is
later deleted, "files/images/" is deleted as well, assuming no other files with
prefix "files/" or "files/images/" were uploaded in the mean time.

This means that we need to be carefull in handling file and prefix names. In
this module, ``prefix`` will always refer to a string ending with a ``/``
character and will represent a directory. ``filename`` will refer to a string
*not* ending with a ``/`` character and represents a file. No path will ever
start with ``/``.

The prefix
----------

When uploading a file, a :attr:`~.FileUpload.prefix` is created which will be
prepended to every file. The prefix consists of 3 parts.

The first part is a system-wide prefix, loaded from
:const:`~odyssey.defaults.AWS_S3_PREFIX`.

The second part is a per-user prefix. The per-user prefix is rendered from the
string template stored in :const:`~odyssey.defaults.AWS_S3_USER_PREFIX`, using
:attr:`user_id` to format the template.

The third part is an extra prefix. It can be thought of as a subdirectory
within the directory of this user. It is set from :attr:`prefix` parameter
supplied to the methods in :class:`FileUpload`.

The final :attr:`.FileUpload.prefix` will be:

.. code-block:: python

    AWS_S3_PREFIX/AWS_S3_USER_PREFIX.format(user_id=user_id)/prefix/

For more on the prefixes, also see :const:`~odyssey.defaults.AWS_S3_BUCKET`,
:const:`~odyssey.defaults.AWS_S3_PREFIX`, and
:const:`~odyssey.defaults.AWS_S3_USER_PREFIX` in the :mod:`odyssey.defaults`
module.
"""

import base64
import hashlib
import logging

from io import BytesIO

import boto3
import filetype

from typing import List
from botocore.exceptions import ClientError
from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.exceptions import BadRequest
from odyssey.api.user.models import UserProfilePictures

from odyssey.utils.constants import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_FILE_TYPES,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_MEDICAL_IMAGE_TYPES,
    AUDIO_MAX_SIZE,
    FILE_MAX_SIZE,
    IMAGE_MAX_SIZE,
    MEDICAL_IMAGE_MAX_SIZE)

logger = logging.getLogger(__name__)


class S3Bucket:
    """ Loads the S3 boto3 resource and an S3 bucket.

    Use this class if you need direct access to the S3 bucket without any of
    the other predefined file upload and download actions.
    """

    def __init__(self):
        """
        This class loads the S3 bucket named by
        :const:`~odyssey.defaults.AWS_S3_BUCKET`. The :mod:`boto3` resource is
        stored as :attr:`~.S3Bucket.s3`. The bucket object is stored as
        :attr:`~.S3Bucket.bucket`.
        """
        bucket_name = current_app.config['AWS_S3_BUCKET']

        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(bucket_name)


class FileDownload(S3Bucket):
    """ Utilities to download or delete files from an AWS S3 bucket.

    This class operates on files that already exist in the S3 bucket. Each
    method requires a ``filename`` parameter, which must be a filename that
    includes the full prefix. A check is performed to make sure the provided
    filename is not outside the system-wide prefix.
    """

    def __init__(self, user_id: int):
        """ Instantiate the :class:`.FileDownload` class.

        Parameters
        ----------
        user_id : int
            The ID number of the user to handle files for.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised when :attr:`user_id` is not valid.
        """
        if not user_id or not isinstance(user_id, int):
            raise BadRequest('User ID must be an integer.')

        super().__init__()
        self.user_id = user_id

        prefix = current_app.config['AWS_S3_PREFIX'].strip('/')
        user_prefix = current_app.config['AWS_S3_USER_PREFIX'].strip('/')

        self.prefix = ''
        if prefix:
            self.prefix += f'{prefix}/'
        if user_prefix:
            self.prefix += user_prefix.format(user_id=user_id) + '/'

    def check_filename(self, filename: str):
        """ Make sure filename starts with self.prefix """
        if self.prefix and not filename.startswith(self.prefix):
            # Logging an extra message, because I don't want to leak info
            # in the user facing error message.
            logger.error(
                f'Trying to access file "{filename}" '
                f'in S3 bucket "{self.bucket.name}" '
                f'while prefix is set to "{self.prefix}".')
            raise BadRequest('Operation not allowed, file outside prefix.')

    def url(self, filename: str, expires: int = 3600) -> str:
        """ Generate a presigned URL for ``filename``.

        A presigned URL can be used to download the file directly from S3.
        The URL expires after ``expires`` seconds (default: 10 min).

        Parameters
        ----------
        filename : str
            The name of the file to generate a URL for.

        expires : int
            The number of seconds after which the generated URL expires.
            Defaults to 3600 (10 min).

        Returns
        -------
        str
            The presigned URL.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised in case of a boto3 error.
        """
        self.check_filename(filename)

        try:
            url = self.s3.meta.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket.name,
                    'Key': filename},
                ExpiresIn=expires)
        except ClientError as err:
            msg = err.response['Error']['Message']
            raise BadRequest(f'AWS returned the following error: {msg}')

        return url
    
    def urls(self, filenames: dict, expires: int = 3600):
        """ Generate a dict of presigned URLs for each ``filename`` in ``filenames``.

        A presigned URL can be used to download the file directly from S3.
        The URL expires after ``expires`` seconds (default: 10 min).

        Parameters
        ----------
        filenames : dict{}
            Contains a list of image paths to be converted to presigned links. The key can be whatever
            is needed for the final products while the values should be image paths to files in s3.

        expires : int
            The number of seconds after which the generated URL expires.
            Defaults to 3600 (10 min).

        Returns
        -------
        list(str)
            The presigned URLs.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised in case of a boto3 error.
        """
    
        urls = {}
        for k, filename in filenames.items():
            #update the image path (value for each key) to be a presigned link
            urls[k] = self.url(filename, expires)
        return urls

    def delete(self, filename: str):
        """ Delete a file.

        Only one file can be deleted per call. An INFO log message is send when
        the file is successfully deleted. If filename is empty, nothing is done
        (no error).

        Parameters
        ----------
        filename : str
            The name of the file to delete.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised in case of a boto3 error.
        """
        self.check_filename(filename)

        if not filename:
            return

        # The output of filter is an objectsCollection, which is an iterator.
        # Iterators have no len() and cannot be sliced.
        objs = tuple(self.bucket.objects.filter(Prefix=filename))

        if len(objs) == 0:
            raise BadRequest(f'Filename {filename} not found.')
        elif len(objs) > 1:
            raise BadRequest(f'Multiple files with name {filename} found.')

        try:
            objs[0].delete()
        except ClientError as err:
            msg = err.response['Error']['Message']
            raise BadRequest(f'AWS returned the following error: {msg}')

        logger.info(f'{filename} deleted from S3 bucket {self.bucket.name}.')


class FileUpload(FileDownload):
    """ Utilities to upload files to an AWS S3 bucket.

    This class operates on newly created files the S3 bucket. Each method
    requires a ``filename`` parameter, which must be a filename without any
    prefixes. Setting the prefix (the directory) where to store the file is
    handled during instantiation of this class.
    """

    max_size = FILE_MAX_SIZE
    allowed_types = ALLOWED_FILE_TYPES

    def __init__(self, file, user_id: int, prefix: str = ''):
        """ Instantiate the :class:`.FileUpload` class.

        Parameters
        ----------
        file : BytesIO or _io.BufferedReader
            A file handle to the uploaded file.

        user_id : int
            The User ID number of the user for whom to handle files on S3.

        prefix : str (default '')
            An additional prefix to append to :attr:`.FileDownload.prefix`.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised if :attr:`file` is not a readable file handle.
        """
        if not (hasattr(file, 'read')
                and hasattr(file, 'tell')
                and hasattr(file, 'seek')):
            return BadRequest('File must be an opened file object.')

        super().__init__(user_id)

        self.file = file
        self.file.seek(0)
        ft = filetype.guess(self.file)
        self.extension = ft.extension
        self.mime = ft.mime
        self.size = self.file.seek(0, 2)
        self.file.seek(0)

        if prefix:
            self.prefix += f'{prefix}/'

        # This will be set only after the file is uploaded to S3.
        self.filename = ''

    def _read_chunk(self, chunk_size=8192) -> bytes:
        """ Read :attr:`.FileUpoad.file` in chunks.

        Reads the entire file. Resets the file position to the beginning of the
        file before the first read and after the last.

        Parameters
        ----------
        chunk_size : int
            Size in bytes of chunk to read. Defaults to 8192 (8 kb).

        Yields
        ------
        bytes
            The bytes read from :attr:`.FileUpoad.file`.
        """
        self.file.seek(0)
        while True:
            data = self.file.read(chunk_size)
            if not data:
                break
            yield data
        self.file.seek(0)

    def parse_filename(self, filename: str, prefix: str = '') -> str:
        """ Validate and clean up filename.

        The following actions will be performed:

        - Check that filename is a string, raise error if not.
        - Strip any leading or trailing / characters.
        - Check that filename is not empty after stripping /, or raise error.
        - Prepend :attr:`prefix` if not empty.
        - Prepend :attr:`.FileDownload.prefix`.

        :attr:`.FileDownload.prefix` will only be added once, so it is safe to
        call this function multiple times on the same filename. The returned
        value will always be the same.

        Parameters
        ----------
        filename : str
            The filename to check.

        prefix : str (default '')
            An additional prefix to append to :attr:`.FileDownload.prefix`.

        Returns
        -------
        str
            The cleaned and validated filename.

        Raises
        ------
        :class:`~werkzeug.exceptions.BadRequest`
            Raised if filename is not a string or if it is empty (after
            removing any leading or trailing / characters).
        """
        if not isinstance(filename, str):
            t = str(type(filename))
            raise BadRequest(f'Filename must be a string, got {t}')

        filename = filename.strip('/')

        if not filename:
            raise BadRequest('Filename can not be empty.')

        prefix = prefix.strip('/')

        if self.prefix and not filename.startswith(self.prefix):
            if prefix:
                prefix = f'{prefix}/'
            filename = f'{self.prefix}{prefix}{filename}'

        return filename

    def validate_size(self) -> bool:
        """ Validate the file size.

        Checks whether :attr:`.FileUpoad.size` does not exceed
        :attr:`.FileUpoad.max_size`.

        Returns
        -------
        bool
            Returns ``False`` if file size exceeds maximum allowed file size,
            ``True`` otherwise.
        """
        return self.size <= self.max_size

    def validate_type(self) -> bool:
        """ Validate the filetype.

        Checks whether :attr:`.FileUpoad.extension` is in
        :attr:`.FileUpoad.allowed_types`. The file extension is determined by
        inspecting the file magic of the binary data stream. It does therefore
        not rely on the file extension or mime type presented to the API by the
        user.

        Returns
        -------
        bool
            Returns ``True`` if :attr:`.FileUpoad.extension` is found in the
            list of :attr:`.FileUpoad.allowed_types`, ``False`` otherwise.
        """
        return self.extension in self.allowed_types

    def validate(self):
        """ Validate both size and type of uploaded file.

        Checks both :meth:`validate_size` and :meth:`validate_type`. Raises
        :exc:`~werkzeug.exceptions.BadRequest` in case either one fails.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised when either :meth:`validate_size` or :meth:`validate_type`
            return False.
        """
        if not self.validate_size():
            pretty = f'{self.max_size} bytes'
            if self.max_size > 1024:
                val = self.max_size / 1024
                pretty = f'{val:0.1f} kb'
            elif self.max_size > 1024 * 1024:
                val = self.max_size / (1024 * 1024)
                pretty = f'{val:0.1f} Mb'
            elif self.max_size > 1024 * 1024 * 1024:
                val = self.max_size / (1024 * 1024 * 1024)
                pretty = f'{val:0.1f} Gb'
            raise BadRequest(f'File exceeds maximum size of {pretty}.')

        if not self.validate_type():
            raise BadRequest(
                f'File recognized as {self.extension} ({self.mime}). '
                'Only allowed are {}'.format(', '.join(self.allowed_types)))

    def save(self, filename: str, prefix: str = ''):
        """ Store the uploaded file on S3 under the given filename.

        After upload is complete, sets :attr:`.FileUpoad.filename` to the full
        path constructed from :attr:`filename` and :attr:`prefix`.

        Parameters
        ----------
        filename : str
            The name to save the file under on S3.

        prefix : str (default '')
            An additional prefix to append to :attr:`.FileDownload.prefix`.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised in case of boto3 errors.
        """
        filename = self.parse_filename(filename, prefix=prefix)

        # Integrity check: AWS automatically verifies md5 checksum if provided.
        md5 = hashlib.md5()
        for data in self._read_chunk():
            md5.update(data)

        md5_b64 = base64.b64encode(md5.digest()).decode('utf-8')

        try:
            self.bucket.put_object(
                Key=filename,
                Body=self.file,
                ContentMD5=md5_b64)
        except ClientError as err:
            msg = err.response['Error']['Message']
            raise BadRequest(f'AWS returned the following error: {msg}')

        self.filename = filename

    def url(self, expires: int = 3600) -> str:
        """ Generate a presigned URL for the uploaded file.

        Same as :meth:`.FileDownload.url` except that
        :attr:`~.FileUpload.filename` is used as a filename. An error will be
        raised if the file was not saved before calling this method.

        .. seealso:: :meth:`.FileDownload.url`
        """
        if not self.filename:
            raise BadRequest(
                'File has not been uploaded to S3 yet, use save() first.')

        return super().url(self.filename, expires=expires)


class AudioUpload(FileUpload):
    """ Utilities to upload audio recordings to an AWS S3 bucket.

    This class is similar to :class:`.FileUpload` except that it validates
    specifically for audio file types.
    """

    max_size = AUDIO_MAX_SIZE
    allowed_types = ALLOWED_AUDIO_TYPES

    def __init__(self, file, user_id: int, prefix: str = ''):
        """ Instantiate the :class:`.AudioUpload` class.

        .. see:: :meth:`.FileUpload.__init__`
        """
        super().__init__(file, user_id, prefix=prefix)

        # Force audio type on extension guessing.
        ft = filetype.audio_match(self.file)
        self.extension = ft.extension
        self.mime = ft.mime


class ImageUpload(FileUpload):
    """ Utilities to upload image files to an AWS S3 bucket.

    This class is similar to :class:`.FileUpload` except that it validates
    specifically for image file types. During instantiation of the class, the
    image is loaded as a :class:`PIL.Image` in :attr:`~.ImageUpload.image`.
    """

    max_size = IMAGE_MAX_SIZE
    allowed_types = ALLOWED_IMAGE_TYPES

    def __init__(self, file, user_id: int, prefix: str = ''):
        """ Instantiate the :class:`.ImageUpload` class.

        .. see:: :meth:`.FileUpload.__init__`
        """
        super().__init__(file, user_id, prefix=prefix)

        self._prefix = prefix

        # Force image type on extension guessing
        ft = filetype.image_match(self.file)
        self.extension = ft.extension
        self.mime = ft.mime

        # Open PIL image for supported formats
        try:
            self.image = Image.open(self.file)
        except UnidentifiedImageError:
            self.image = None
            self.width = 0
            self.height = 0
        else:
            # Rotate image in case EXIF tags have a orientation
            self.image = ImageOps.exif_transpose(self.image)

            self.width, self.height = self.image.size

    def _pil_to_imageupload(self, image: Image, **kwargs):
        """ Convert a PIL image to a new instance of ImageUpload. """
        # Remove transparency
        if (image.mode in ('RGBA', 'LA')
            or (image.mode == 'P'
                and 'transparency' in image.info)):
            image = image.convert('RGB')

        if 'format' not in kwargs:
            kwargs['format'] = 'jpeg'
            if 'quality' not in kwargs:
                kwargs['quality'] = 90

        buf = BytesIO()
        image.save(buf, **kwargs)
        buf.seek(0)

        imgupl = ImageUpload(buf, self.user_id, prefix=self._prefix)

        # Set image to PIL image, to prevent quality loss due to jpeg roundtrip
        imgupl.image = image

        return imgupl

    def resize(self, dimensions: tuple, **kwargs):
        """ Resize image to ``dimension``.

        Resizes :attr:`.ImageUpload.file` to the given dimension. If the
        original image is not square, it will crop the image to a square before
        resizing.

        Parameters
        ----------
        dimensions : tuple(int, int)
            The (width, height) tuple of the new image.

        **kwargs
            Any additional parameters are passed to :meth:`PIL.Image.save`.
            They default to ``format='jpeg', quality=90``.

        Returns
        -------
        :class:`.ImageUpload`
            A new instance of :class:`.ImageUpload` with
            :attr:`~.ImageUpload.file` and :attr:`~.ImageUpload.image` set to
            the cropped image.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised in case dimensions is not of shape tuple(int, int).
        """
        if (not isinstance(dimensions, (tuple, list))
                or len(dimensions) != 2
                or not isinstance(dimensions[0], int)
                or not isinstance(dimensions[1], int)):
            raise BadRequest('Dimensions must be a tuple of 2 integers.')

        box = None
        if self.width != self.height:
            long_side = max(self.width, self.height)
            short_side = min(self.width, self.height)
            crop_len = (long_side - short_side) // 2

            # Extra pixel in case long_side has odd number of pixels.
            extra = long_side % 2

            # Landscape or portrait; box is left, top, right, bottom.
            if self.width > self.height:
                box = (crop_len, 0, self.width - crop_len - extra, self.height)
            else:
                box = (0, crop_len, self.width, self.height - crop_len - extra)

        resized = self.image.resize(dimensions, box=box, reducing_gap=2.0)

        return self._pil_to_imageupload(resized, **kwargs)


# TODO: finish work on this class.
# I want this class to work like ImageUpload (with resize()) for raster
# images and like generic FileUpload for other file types (pdf, dicom).
# Need to play around more with multiple inheritance and mixins to get
# this to work.
class MedicalImageUpload(ImageUpload, FileUpload):
    """ Utilities to upload medical images to an AWS S3 bucket.

    This class is similar to :class:`.ImageUpload` except that it includes PDF
    files and DICOM images as allowed images types. The maximum file size is
    also larger that regular images.
    """
    max_size = MEDICAL_IMAGE_MAX_SIZE
    allowed_types = ALLOWED_MEDICAL_IMAGE_TYPES

    def __init__(self, file, user_id: int, prefix: str = ''):
        """ Instantiate the :class:`.MedicalImageUpload` class.

        .. see:: :meth:`.ImageUpload.__init__`
        """
        # Create set of matchers, unique and remove None.
        matchers = {filetype.get_type(t) for t in ALLOWED_MEDICAL_IMAGE_TYPES}
        matchers = matchers - {None}

        ft = filetype.match(self.file, matchers=matchers)
        self.extension = ft.extension
        self.mime = ft.mime

        if self.extension in ('pdf', 'dcm'):
            super(FileUpload, self).__init__(file, user_id, prefix=prefix)
        else:
            super(ImageUpload).__init__(file, user_id, prefix=prefix)

def get_profile_pictures(user_id : int, is_staff: bool):
    """ Gets a dict of resized profile pictures
    
    Returns a dict of resized profile pictures for the given ``user_id`` and ``is_staff`` 
    status in the format {(picture width): (presigned url)}.
    
     Parameters
        ----------
        user_id : int
            User id of the user to fetch the profile pictures of.

        is_staff : bool
            Denotes if the staff or client profile pictures should be fetched for the given user id.

        Returns
        -------
        dict{str: str} : 
            The strigified image width and the presigned url.

        Raises
        ------
        :exc:`~werkzeug.exceptions.BadRequest`
            Raised in case dimensions is not of shape tuple(int, int).
    """
    if is_staff:
        pics = UserProfilePictures.query.filter_by(staff_user_id=user_id).all()
    else:
        pics = UserProfilePictures.query.filter_by(client_user_id=user_id).all()
        
    urls = {}
    if not pics:
        return urls
    
    fd = FileDownload(user_id)
    for pic in pics:
        if pic.original:
            continue
        urls[str(pic.width)] = fd.url(pic.image_path)
        
    return urls