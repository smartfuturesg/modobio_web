import os
import boto3
import mimetypes
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from io import BytesIO

from flask import current_app
from werkzeug.datastructures import FileStorage

from odyssey.utils.constants import ALLOWED_IMAGE_TYPES

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
            raise BadRequest(f'{file_extension} is not an allowed file type. Allowed types are {allowed_file_types}')

        return file_extension

    def validate_file_size(self, file: FileStorage, max_file_size):
        # validate file size is below max_file_size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        if file_size > max_file_size:
            raise BadRequest('File too large')

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
        if file.content_type != 'application/pdf':
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

