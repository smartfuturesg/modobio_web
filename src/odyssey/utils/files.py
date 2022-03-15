""" File storage utilities.

This module handles various aspects of file storage such as validation,
storing to, and retrieving from AWS S3.

S3's top level division is the bucket. Buckets contain objects. Each
object has a unique key. Keys may contain / characters, which make keys
look like a directory structure. In the AWS S3 console, objects with /
characters are indeed displayed as files and directories, but under the
hood they act differently.

There is no way to distinguish an object with key ``/path/file`` from
``/path/file/``. There is no ``is_file()`` method or attribute to distinguish
the first from the latter. But both objects can exist at the same time.
This means that we need to be carefull in handling file and prefix names.

In this module, ``prefix`` will always refer to a string ending in / and
will represent a directory. ``filename`` will refer to a string *not*
ending in / and will represent a file.
"""

import base64
import hashlib
import logging

from io import BytesIO

import boto3
import filetype

from botocore.exceptions import ClientError
from flask import current_app
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from odyssey.utils.constants import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_FILE_TYPES,
    ALLOWED_IMAGE_TYPES,
    AUDIO_MAX_SIZE,
    FILE_MAX_SIZE,
    IMAGE_MAX_SIZE)

logger = logging.getLogger(__name__)


class S3Bucket:
    """ Class that establishes a connection to an AWS S3 bucket. """

    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.s3_bucket_name = current_app.config['AWS_S3_BUCKET']
        self.s3_bucket = self.s3.Bucket(self.s3_bucket_name)

        self.s3_prefix = current_app.config['AWS_S3_PREFIX']
        if self.s3_prefix and not self.s3_prefix.endswith('/'):
            self.s3_prefix += '/'

        logger.debug(f'S3 bucket name: {self.s3_bucket_name}')
        logger.debug(f'S3 bucket prefix: {self.s3_prefix}')


class FileDownload(S3Bucket):
    def parse_filename(self, filename: str) -> str:
        """ Validate and clean up filename.

        The following actions will be performed:

        - Check that filename is a string, raise error if not.
        - Check that filename is not empty, raise error if it is.
        - Strip any leading or trailing / characters.
        - Prepend :attr:`~.S3Bucket.s3_prefix`.

        :attr:`~.S3Bucket.s3_prefix` will only be added once, so it is safe to call
        this function multiple times on the same filename. The returned value will
        always be the same.

        Parameters
        ----------
        filename : str
            The filename to check.

        Returns
        -------
        str
            The cleaned and validated filename.

        Raises
        ------
        :class:`~werkzeug.exceptions.BadRequest`
            Raised if filename is not a string or if it is empty (after removing
            any leading or trailing / characters).
        """
        if not isinstance(filename, str):
            raise BadRequest('Filename must be a string, got ' + str(type(filename)))

        filename = filename.strip('/')

        if not filename:
            raise BadRequest('Filename can not be empty.')

        if self.s3_prefix and not filename.startswith(self.s3_prefix):
            filename = self.s3_prefix + filename

        return filename

    def parse_prefix(self, prefix: str) -> str:
        """ Validate and clean up filename.

        Same as :meth:`~.FileDownload.parse_filename` except that a prefix
        will always end (but not start) with a / character.

        .. seealso:: :meth:`.S3Upload.parse_filename`
        """
        return self.parse_filename(prefix) + '/'

    def url(self, filename: str, expires: int=3600) -> str:
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
        :class:`~werkzeug.exceptions.BadRequest`
            Raised in case of a boto3 error.
        """
        filename = self.parse_filename(filename)

        try:
            url = self.s3.meta.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.s3_bucket_name,
                    'Key': filename},
                ExpiresIn=expires)
        except ClientError as err:
            raise BadRequest('AWS returned the following error: ' + err.response['Error']['Message'])

        return url

    # def all_urls(self, prefix: str, expires: int=3600) -> dict:
    #     """ Generate a URL for every object at with the same prefix.
    #
    #     Just like :meth:`~.FileDownload.url` but for all objects (files) with the
    #     same prefix (in this directory).
    #
    #     .. seealso:: :meth:`.FileDownload.url`
    #
    #     Parameters
    #     ----------
    #     prefix : str
    #         URLs will be generated for all keys that share the same prefix,
    #         i.e. all files in this directory.
    #
    #     expires : int
    #         The number of seconds after which the generated URLs expire.
    #         Defaults to 3600 (10 min).
    #
    #     Returns
    #     -------
    #     dict
    #         A dictionary with filenames as keys and the corresponding
    #         presigned URLs as values.
    #
    #     Raises
    #     ------
    #     :class:`~werkzeug.exceptions.BadRequest`
    #         Raised in case of a boto3 error.
    #     """
    #     prefix = self.parse_prefix(prefix)
    #
    #     objs = self.s3_bucket.objects.filter(Prefix=prefix)
    #
    #     urls = {}
    #     for obj in objs:
    #         url = self.url(obj.key, expires=expires)
    #         urls[obj.key] = url
    #
    #     return urls

    def delete(self, filename: str):
        """ Delete a file """
        filename = self.parse_filename(filename)

        # The output of filter is an objectsCollection, which is an iterator.
        # Iterators have no len() and cannot be sliced.
        objs = tuple(self.s3_bucket.objects.filter(Prefix=filename))
        
        if len(objs) == 0:
            BadRequest(f'Filename {filename} not found.')
        elif len(objs) > 1:
            BadRequest('Multiple files with name {filename} found.')

        try:
            objs[0].delete()
        except ClientError as err:
            raise BadRequest('AWS returned the following error: ' + err.response['Error']['Message'])

        logger.info(f'File {filename} deleted.')


class FileUpload(FileDownload):
    """ Methods for validating and storing uploaded files. """

    max_size = FILE_MAX_SIZE
    allowed_types = ALLOWED_FILE_TYPES

    def __init__(self, file: FileStorage):
        """ Initialize the FileUpload instance.

        Parameters
        ----------
        file : :class:`~werkzeug.datastructures.FileStorage`
            The uploaded file wrapped by :class:`~werkzeug.datastructures.FileStorage`.

        Raises
        ------
        TypeError
            Raised if :attr:`file` is not a :class:`~werkzeug.datastructures.FileStorage`.
        """
        super().__init__()

        if not isinstance(file, FileStorage):
            return TypeError('File must be wrapped in werkzeug FileStorage.')

        self.file = file
        self.file.stream.seek(0)
        ft = filetype.guess(self.file.stream)
        self.extension = ft.extension
        self.mime = ft.mime
        self.size = self.file.stream.seek(0, 2)
        self.file.stream.seek(0)

        # This will be set only after the file is uploaded to S3.
        # It will never include the s3_prefix.
        self.filename = ''

    def _read_chunk(self, chunk_size=8192) -> bytes:
        """ Read :attr:`.FileUpoad.file.stream` in chunks.

        Reads the entire file. Resets the file position to the beginning
        of the file before the first read and after the last.

        Parameters
        ----------
        chunk_size : int
            Size in bytes of chunk to read. Defaults to 8192 (8 kb).

        Yields
        ------
        bytes
            The bytes read from :attr:`.FileUpoad.file.stream`.
        """
        self.file.seek(0)
        while True:
            data = self.file.stream.read(chunk_size)
            if not data:
                break
            yield data
        self.file.seek(0)

    def validate_size(self) -> bool:
        """ Validate the file size.

        Checks whether :attr:`.FileUpoad.size` does not exceed :attr:`.FileUpoad.max_size`.

        Returns
        -------
        bool
            Returns ``False`` if file size exceeds maximum allowed file size, ``True`` otherwise.
        """
        return self.size <= self.max_size

    def validate_type(self) -> bool:
        """ Validate the filetype.

        Checks whether :attr:`.FileUpoad.extension` is in :attr:`.FileUpoad.allowed_types`.
        The file extension is determined by inspecting the file magic of the binary
        data stream. It does therefore not rely on the file extension or mime type
        presented to the API by the user.

        Returns
        -------
        bool
            Returns ``True`` if :attr:`.FileUpoad.extension` is found in the list of
            :attr:`.FileUpoad.allowed_types`, ``False`` otherwise.
        """
        return self.extension in self.allowed_types

    def validate(self):
        """ Validate both size and type of uploaded file.

        Checks both :meth:`validate_size` and :meth:`validate_type`. Raises
        :class:`~werkzeug.exceptions.BadRequest` in case either one fails.

        Raises
        ------
        :class:`~werkzeug.exceptions.BadRequest`
            Raised when either :meth:`validate_size` or :meth:`validate_type` fail.
        """
        if not self.validate_size():
            pretty = f'{self.max_size} bytes'
            if self.max_size > 1024:
                val = self.max_size / 1024
                pretty = '{val:0.1f} kb'
            elif self.max_size > 1024 * 1024:
                val = self.max_size / (1024 * 1024)
                pretty = '{val:0.1f} Mb'
            elif self.max_size > 1024 * 1024 * 1024:
                val = self.max_size / (1024 * 1024 * 1024)
                pretty = '{val:0.1f} Gb'
            raise BadRequest(f'File exceeds maximum size of {pretty}.')

        if not self.validate_type():
            raise BadRequest(f'File recognized as {self.extension} ({self.mime}). '
                              'Only allowed are {}'.format(', '.join(self.allowed_types)))

    def save(self, filename: str):
        """ Store the uploaded file on S3 under the given filename.

        After upload is complete, sets :attr:`.FileUpoad.filename` to the
        given filename.

        Parameters
        ----------
        filename : str
            The name to save the file under on S3.

        Raises
        ------
        :class:`~werkzeug.exceptions.BadRequest`
            Raised in case of boto3 errors or file corruption during upload.
        """
        filename = self.parse_filename(filename)

        # TODO: Why an exception for PDF files?
        # if self.file.content_type != 'application/pdf':
        #     self.file.seek(0)

        # Integrity check: AWS automatically verifies md5 checksum if provided.
        md5 = hashlib.md5()
        for data in self._read_chunk():
            md5.update(data)

        md5_b64 = base64.b64encode(md5.digest()).decode('utf-8')

        try:
            ret = self.s3_bucket.put_object(
                Key=filename,
                Body=self.file.stream,
                ContentMD5=md5_b64)
        except ClientError as err:
            raise BadRequest('AWS returned the following error: ' + err.response['Error']['Message'])

        self.filename = filename

    def url(self, expires: int=3600) -> str:
        """ Generate a presigned URL for the just uploaded file.

        Same as :meth:`S3Bucket.url` except that an error will be 
        the file was not saved before calling this method.

        .. seealso:: :meth:`S3Bucket.url`
        """
        if not self.filename:
            raise BadRequest('File has not been uploaded to S3 yet, use save() first.')

        return super().url(self.filename, expires=expires)


class AudioUpload(FileUpload):
    """ Methods for validating and storing uploaded audio files. """

    max_size = IMAGE_MAX_SIZE
    allowed_types = ALLOWED_IMAGE_TYPES

    def __init__(self, file: FileStorage):
        super().__init__(file)

        # Force audio type on extension
        ft = filetype.audio_match(self.file.stream)
        self.extension = ft.extension
        self.mime = ft.mime


class ImageUpload(FileUpload):
    """ Methods for validating and storing uploaded image files. """

    max_size = IMAGE_MAX_SIZE
    allowed_types = ALLOWED_IMAGE_TYPES

    def __init__(self, file: FileStorage):
        super().__init__(file)

        # Force image type on extension
        ft = filetype.image_match(self.file.stream)
        self.extension = ft.extension
        self.mime = ft.mime
        self.validate()

        # Open PIL image
        self.image = Image.open(self.file.stream)
        self.width, self.height = self.image.size

    def crop(self):
        """ Crop image.

        Crops :attr:`.ImageUpload.file` to a square image. Then converts the
        image to JPEG format. Any transparency (in case of an uploaded PNG
        file), is discarded.

        Returns
        -------
        ImageUpload
            A new instance of :class:`ImageUpload` with :attr:`~.ImageUpload.file`
            set to the cropped image.
        """
        image = self.image.copy()
        # If image is not a square, find the shortest side and crop to that length.
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

            image = image.crop(box)

        # Force transparent PNGs to a non-transparent RGB palette.
        if self.extension == 'png':
            image = image.convert('RGB')

        # Always save as JPEG.
        buf = BytesIO()
        image.save(buf, format='jpeg', quality=90)
        buf.seek(0)

        f = FileStorage(
            stream=buf,
            filename='squared.jpg',
            content_type='image/jpeg')
        return ImageUpload(f)

    def resize(self, dimensions: tuple):
        """ Resize image to ``dimension``.

        Resizes :attr:`.ImageUpload.file` to the given dimension. Then
        converts the image to JPEG format. Any transparency (in case of
        an uploaded PNG file), is discarded.

        Parameters
        ----------
        dimensions : tuple(int, int)
            The (length, width) tuple of the new image.

        Returns
        -------
        ImageUpload
            A new instance of :class:`ImageUpload` with :attr:`~.ImageUpload.file`
            set to the resized image.

        Raises
        ------
        :class:`~werkzeug.exceptions.BadRequest`
            Raised in case dimensions is not of shape tuple(int, int).
        """
        if (not isinstance(dimensions, (tuple, list)) or
            len(dimensions) != 2 or
            not isinstance(dimensions[0], int) or
            not isinstance(dimensions[1], int)):
            raise BadRequest('Dimensions must be a tuple of 2 integers.')

        image = self.image.copy()
        image.thumbnail(dimensions)

        buf = BytesIO()
        if self.extension == 'png':
            image = image.convert('RGB')

        image.save(buf, format='jpeg', quality=90)

        f = FileStorage(
            stream=buf,
            filename=f'size{dimensions[0]}x{dimensions[1]}.jpg',
            content_type='image/jpeg')

        return ImageUpload(f)
