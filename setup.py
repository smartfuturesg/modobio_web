#!/usr/bin/env python
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as fh:
    long_description = fh.read()

with open(os.path.join(here, 'src', 'odyssey', '__init__.py')) as fh:
    for line in fh:
        if line.startswith('__version__'):
            __version__ = line.split('=')[-1].strip().strip("'")
            break

setup(
    name='odyssey',
    version=__version__,
    description='Staff application to guide the client journey.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.atventurepartners.tech/zan/odyssey',
    author='zan',
    author_email='zan.peeters@atventurepartners.tech',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=[
        'boto3',
        'Flask',
        'Flask-Cors',
        'Flask-HTTPAuth',
        'Flask-Migrate',
        'flask-restx',
        'Flask_SQLAlchemy',
        'Flask_WeasyPrint',
        'Flask_WTF',
        'pytest',
        'pytest-cov',
        'pytz',
        'WTForms',
    ],
    include_package_data=True
)
