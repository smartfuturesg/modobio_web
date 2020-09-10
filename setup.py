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
        'Flask',
        'flask-accepts',
        'Flask-Cors',
        'Flask-HTTPAuth',
        'flask-marshmallow',
        'Flask-Migrate',
        'flask-restx',
        'Flask_SQLAlchemy',
        'Flask_WTF',
        'marshmallow',
        'marshmallow-sqlalchemy',
        'PyPDF2',
        'pytest',
        'pytest-cov',
        'pytz',
        'psycopg2',
        'requests-oauthlib',
        'WeasyPrint',
        'WTForms',
    ],
    include_package_data=True
)
