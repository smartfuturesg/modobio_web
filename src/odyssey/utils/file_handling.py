import logging
import os

from io import BytesIO

import boto3
import filetype

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


class FileUpload:
    """ Methods for validating and storing uploaded files. """

    max_size = FILE_MAX_SIZE
    allowed_type = ALLOWED_FILE_TYPES

    def __init__(self, file: FileStorage):
        """ Initialize the File object.

        Instantiates the File object and loads the AWS S3 bucket for
        file storing.

        Parameters
        ----------
        file : :class:`werkzeug.datastructures.FileStorage`
            The uploaded file wrapped by :class:`werkzeug.datastructures.FileStorage`.
        """
        if not isinstance(file, FileStorage):
            return TypeError('File must be wrapped in werkzeug FileStorage.')

        self.file = file
        self.extension = filetypes.guess(self.file.stream)

        self.s3 = boto3.resource('s3')
        self.s3_bucket_name = current_app.config['AWS_S3_BUCKET']
        self.s3_prefix = current_app.config['AWS_S3_PREFIX']
        if self.s3_prefix and not self.s3_prefix.endswith('/'):
            self.s3_prefix += '/'
        self.s3_bucket = self.s3.Bucket(self.s3_bucket_name)

        logger.debug(f'S3 bucket name: {self.s3_bucket_name}')
        logger.debug(f'S3 bucket prefix: {self.s3_prefix}')

    def validate_file_size(self) -> bool:
        """ Makes sure the given file does not exceed a given maximum file size.

        Parameters
        ----------
        file_ : :class:`werkzeug.datastructures.FileStorage`
            The uploaded file.

        Returns
        -------
        bool
            Returns False if file size exceeds maximum allowed file size, True otherwise.
        """
        self.file.seek(0, os.SEEK_END)
        file_size = self.file.tell()

        if file_size > self.max_file_size:
            return False
        return True

    def validate_file_type(self) -> bool:
        """ Extract and validate the filetype.

        Uses :mod:`filetypes` package to inspect the file magic of the binary data stream.
        That way it does not rely on input provided by the same source who sends the file.

        Parameters
        ----------
        file_ : :class:`werkzeug.datastructures.FileStorage`
            The uploaded file as wrapped by werkzeug.

        allowed_file_types : tuple
            List of file extensions allowed in the processing of this file. Give extensions
            as a tuple of strings, including the '.'.

        Returns
        -------
        bool
            The correct extensions of the file as inferred from the binary file magic.
        """
        if self.extension in self.allowed_file_types:
            return True
        return False

    def save_to_s3(self, filename: str):
        # TODO: docstring
        # TODO: Why an exception for PDF files?
        if self.file.content_type != 'application/pdf':
            self.file.seek(0)

        try:
            self.s3_bucket.put_object(
                Key=self.s3_prefix + filename,
                Body=self.file.stream)
        except Exception as e:
            # TODO: raise error
            logger.error(f'S3 error when saving file: {e}')

    def get_presigned_urls(self, prefix: str) -> dict:
        # TODO: docstring + better way?
        # TODO: find a way o deal with multiple files.
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
        # TODO: docstring
        # returns a single url with defined file_path
        # if file_path doesn't exists in S3, it will return an empty string
        params = {'Bucket': self.s3_bucket_name}
        url = ''
        for file in self.s3_bucket.objects.filter(Prefix=self.s3_prefix + file_path):
            params['Key'] = file.key
            url = self.s3_resource.meta.client.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)
        return url

    def delete_from_s3(self, prefix):
        # TODO: docstring
        try:
            self.s3_bucket.objects.filter(Prefix=self.s3_prefix + prefix).delete()
        except Exception as e:
            logger.error(f'S3 error when deleting file: {e}')


class ImageUpload(FileUpload):
    """ Methods for validating and storing uploaded image files. """

    max_size = IMAGE_MAX_SIZE
    allowed_type = ALLOWED_IMAGE_TYPES

    def crop(self) -> FileStorage:
        # TODO: docstring, store output in instance.
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

    def resize(self, dimensions: tuple) -> Image:
        # TODO convert + docstring
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


class AudioUpload(FileUpload):
    """ Methods for validating and storing uploaded audio files. """

    max_size = IMAGE_MAX_SIZE
    allowed_type = ALLOWED_IMAGE_TYPES
