#!/usr/bin/env python
from setuptools import setup, find_packages
import pathlib

readme = pathlib.Path(__file__).parent / 'README.md'
with open(readme) as fh:
    long_description = fh.read()

setup(
    name='odyssey',
    description='Staff application to guide the client journey.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.atventurepartners.tech/zan/odyssey',
    author='zan',
    author_email='zan.peeters@atventurepartners.tech',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    install_requires=[
        'boto3',
        'celery',
        'celery-redbeat',
        'elasticsearch',
        'filetype',
        'Flask',
        'flask-accepts',
        'Flask-Cors',
        'flask-marshmallow',
        'Flask-Migrate',
        'Flask-PyMongo',
        'flask-restx',
        'Flask_SQLAlchemy',
        'idna',
        'marshmallow',
        'marshmallow-sqlalchemy',
        'psycopg2',        
        'PyPDF2',
        'pytz',
        'redis',
        'requests',
        'requests-oauthlib',
        'twilio',
        'PyJWT',
        'WeasyPrint'
    ],
    include_package_data=True
)
