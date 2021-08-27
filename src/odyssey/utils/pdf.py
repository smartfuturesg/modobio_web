"""
This module handles the generation and storage of PDF files for signed documents.
"""
import logging
logger = logging.getLogger(__name__)

import boto3
import concurrent.futures
import hashlib
import io
import pathlib

from datetime import date
from typing import Type

from botocore.exceptions import ClientError
from flask import render_template, session, current_app, _request_ctx_stack
from PyPDF2 import PdfFileMerger
from weasyprint import HTML, CSS

from odyssey import db
from odyssey.api.client.models import ClientInfo

_executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix='PDF_')

def to_pdf(user_id: int,
           table: Type[db.Model],
           template: str=None,
           form=None):
    """ Generate and store a PDF file from a signed document.

    PDF generation and storage is done in a separate thread in a 'fire-and-forget'
    style, so that this process is non-blocking.

    Parameters
    ----------
    user_id : int
        User ID number.

    table : :class:`flask_sqlalchemy.SQLAlchemy.Model`
        Table that stores information for the document about to be PDFed. Must be
        one of the models in :mod:`odyssey.models.client`.

    template : str
        Filename of the Flask template for which a PDF file is requested.
        If template=None, it is assumed that the HTML comes from the React frontend.
        This is not yet supported.

    form : :attr:`flask.Request.form`
        Form data needed to fill out the forms in the given template.
        If template is not None, form **must** also be given and can not be None.

    Raises
    ------
    ValueError
        Raised when :attr:`user_id` does not exist in a database table.
    """
    # The second argument (first argument to _to_pdf) is key: we need to copy
    # the current RequestContext and pass it to the thread to ensure that the
    # other thread has the same information as the calling thread. Calling the
    # RequestContext in a 'with' statement, also sets the AppContext, which in
    # turn sets current_app to the right value.
    #
    # However, we cannot just pass the RequestContext, it must be a copy. The
    # main thread keeps working and tries to delete the RequestContext when it
    # is finished, while the pdf thread is still running. This leads to
    # AssertionError: popped wrong app context <x> in stead of <y>.
    _executor.submit(
        _to_pdf,
        _request_ctx_stack.top.copy(),
        user_id,
        table,
        template=template,
        form=form
    )

def _to_pdf(req_ctx, user_id, table, template=None, form=None):
    """ Generate and store a PDF file from a signed document.

    Don't call this function directly, use :func:`to_pdf` for non-blocking,
    multi-threaded operation.
    """
    # Even though the db.session instance created by Flask-SQLAlchemy is
    # a 'scoped_session', it is still thread_local. Create a new session,
    # local to this thread, with the same configuration.
    local_session = db.create_scoped_session()
    with req_ctx:
        ### Load data and perform checks
        client = local_session.query(ClientInfo).filter_by(user_id=user_id).one_or_none()

        if not client:
            # Calling thread has already finished, so raising errors here
            # has no effect. Print to stdout instead and hope somebody reads it.
            # TODO: logging
            print(f'User ID {user_id} not found in table {ClientInfo.__tablename__}.')
            return

        query = (
            local_session
            .query(table)
            .filter_by(user_id=user_id)
            .order_by(table.idx.desc())
        )
        doc = query.first()

        if not doc:
            print(f'User ID {user_id} not found in table {table.__tablename__}.')
            return

        if doc.pdf_path:
            # PDF already exists, won't save again
            return

        ### Read HTML page
        if template:
            session['staff_id'] = 1
            #session['clientname'] = client.fullname
            session['user_id'] = user_id

            cssfile = pathlib.Path(__file__).parent.parent / 'legacy' / 'static' / 'style.css'
            css = CSS(filename=cssfile)

            html = render_template(template, form=form, pdf=True)
        else:
            # TODO: get html of page from React frontend
            css = CSS(string='')
            html = '<html><head></head><body>Nothing here yet</body></html>'

        ### Generate PDF document
        pdf = HTML(string=html).write_pdf(stylesheets=[css])
        pdf_hash = hashlib.sha1(pdf).hexdigest()

        user_id = int(user_id)
        docname = table.displayname.split()[0].lower()

        bucket = current_app.config['AWS_S3_BUCKET']
        prefix = current_app.config['AWS_S3_PREFIX']

        filename = f'ModoBio_{docname}_v{doc.revision}_client{user_id:05d}_{doc.signdate}.pdf'
        pdf_path = f'{prefix}/id{user_id:05d}/signed_documents/{filename}'

        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket)
        bucket.put_object(Body=pdf, Key=pdf_path)

        doc.pdf_path = pdf_path
        doc.pdf_hash = pdf_hash
        local_session.commit()

    local_session.remove()

def merge_pdfs(documents: list, user_id: int) -> str:
    """ Merge multiple pdf files into a single pdf.

    Generated document is stored in an S3 bucket with a temp prefix. It expires
    after 1 day. The link to the generated document expires after 10 minutes.

    Parameters
    ----------
    documents : list(str)
        List of links where PDF documents are stored.

    Returns
    -------
    str
        Link to merged PDF file.
    """
    bucket_name = current_app.config['AWS_S3_BUCKET']

    merger = PdfFileMerger()
    bufs = []
    s3 = boto3.client('s3')
    for doc in documents:
        doc_buf = io.BytesIO()
        try:
            s3.download_fileobj(bucket_name, doc, doc_buf)
        except ClientError as e:
            print(f'Could not download file {doc} from S3 bucket {bucket_name}: {e}')
            continue
        doc_buf.seek(0)
        bufs.append(doc_buf)
        merger.append(doc_buf)

    pdf_buf = io.BytesIO()
    merger.write(pdf_buf)
    merger.close()
    for buf in bufs:
        buf.close()
    pdf_buf.seek(0)

    user_id = int(user_id)
    signdate = date.today().isoformat()
    filename = f'ModoBio_client{user_id:05d}_{signdate}.pdf'

    # Anything with a 'temp/' prefix in this bucket is set to be deleted after 1 day.
    fullname = f'temp/{filename}'

    s3 = boto3.client('s3')
    s3.upload_fileobj(pdf_buf, bucket_name, fullname)

    params = {
        'Bucket': bucket_name,
        'Key': fullname}
    pdf_path = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=3600)

    return pdf_path
