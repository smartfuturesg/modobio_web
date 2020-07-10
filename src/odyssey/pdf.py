"""
This module handles the generation and storage of PDF files for signed documents.
"""

import boto3
import io
import os
import pathlib
import threading

from flask import render_template, session
from flask_wtf import FlaskForm
from flask_weasyprint import HTML, CSS

from odyssey import db, create_app
from odyssey.constants import DOCTYPE, DOCTYPE_TABLE_MAP, DOCTYPE_DOCREV_MAP
from odyssey.api.errors import UserNotFound
from odyssey.models.intake import *


def to_pdf(clientid: int,
           doctype: DOCTYPE,
           template: str=None,
           form: FlaskForm=None):
    """ Generate and store a PDF file from a signed document.

    PDF generation and storage is done in a separate thread in a 'fire-and-forget'
    style, so that this process is non-blocking.

    Parameters
    ----------
    clientid : int
        Client ID number.

    doctype : :class:`odyssey.constants.DOCTYPE`
        The type of document that is being processed. Must be a member of
        :class:`odyssey.constants.DOCTYPES`, e.g. `DOCTYPE.consent`

    template : str
        Filename of the Flask template for which a PDF file is requested.
        If template=None, it is assumed that the HTML comes from the React frontend.
        This is not yet supported.

    form : :class:`flask.FlaskForm`
        :class:`flask.Request.form` data needed to fill out the template.
        If :attr:`template` is not None, form *must* also be given and can not be None.

    Raises
    ------
    UserNotFound
        Raised when :attr:`clientid` does not exist in the database,
        or when :attr:`clientid` does not exist in the database table
        corresponding to the given :attr:`doctype`.

    ValueError
        Raised when incorrect :const:`DOCTYPE` is passed.
    """
    thread = threading.Thread(target=_to_pdf,
                              args=(clientid, doctype),
                              kwargs={'template': template, 'form': form})
    thread.start()


def _to_pdf(clientid: int, doctype: DOCTYPE, template: str=None, form: FlaskForm=None):
    """PDF generation for the API/React based app"""
    app = create_app()
    with app.test_request_context():
        client = ClientInfo.query.filter_by(clientid=clientid).one_or_none()
        if not client:
            raise UserNotFound(clientid)

        if not (isinstance(doctype, DOCTYPE) and doctype in DOCTYPE):
            raise ValueError('Doctype {doctype} is not valid. See constants.DOCTYPES.')

        doctable = DOCTYPE_TABLE_MAP[doctype]

        doc = doctable.query.filter_by(clientid=clientid).order_by(doctable.revision.desc()).first()
        if not doc:
            raise UserNotFound(clientid, 'Clientid {clientid} not found in table {doctable.__tablename__}.')

        if doc.url:
            # URL already exists, won't save again
            return

        cssfile = pathlib.Path(__file__).parent / 'static' / 'style.css'
        css = CSS(filename=cssfile)

        if template:
            session['staffid'] = 1
            session['clientname'] = client.fullname
            session['clientid'] = clientid

            html = render_template(template, form=form, pdf=True)
        else:
            # TODO: get html of page from React frontend
            html = '<html><head></head><body>Nothing here yet</body></html>'

        pdf = HTML(string=html).write_pdf(stylesheets=[css])

        clientid = int(clientid)

        filename = f'ModoBio_{doctype.name}_v{doc.revision}_client{clientid:05d}_{doc.signdate}.pdf'
        bucket_name = app.config['DOCS_BUCKET_NAME']

        if app.config['DOCS_STORE_LOCAL']:
            path = pathlib.Path(bucket_name)
            path.mkdir(parents=True, exist_ok=True)

            fullname = path / filename

            with open(fullname, mode='wb') as fh:
                fh.write(pdf)

            url = fullname.as_uri()
        else:
            pdf_obj = io.BytesIO(pdf)
            path = f'id{clientid:05d}/{filename}'

            s3 = boto3.client('s3')
            s3.upload_fileobj(pdf_obj, bucket_name, path)

            region = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
            url = f'https://{bucket_name}.s3.{region}.amazonaws.com/{path}'

        doc.url = url
        db.session.commit()

        if app.config['DEBUG']:
            print('PDF stored at:', url)
