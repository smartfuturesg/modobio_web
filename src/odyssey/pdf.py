"""
This module handles the generation and storage of PDF files for signed documents.
"""

import boto3
import concurrent.futures
import hashlib
import io
import pathlib

from datetime import date
from flask import render_template, session, current_app, _request_ctx_stack
from flask_wtf import FlaskForm
from PyPDF2 import PdfFileMerger
from weasyprint import HTML, CSS

from odyssey import db
from odyssey.constants import DOCTYPE, DOCTYPE_TABLE_MAP, DOCTYPE_DOCREV_MAP
from odyssey.models.client import *

_executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix='PDF_')

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
        :class:`odyssey.constants.DOCTYPE`, e.g. ``DOCTYPE.consent``.

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
        Raised when :attr:`clientid` does not exist in a database table.
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
    # if current_app.testing:
    _executor.submit(
        _to_pdf,
        _request_ctx_stack.top.copy(),
        clientid,
        doctype,
        template=template,
        form=form
    )

def _to_pdf(req_ctx, clientid: int, doctype: DOCTYPE, template: str=None, form: FlaskForm=None):
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
        client = local_session.query(ClientInfo).filter_by(clientid=clientid).one_or_none()

        if not client:
            # Calling thread has already finished, so raising errors here
            # has no effect. Print to stdout instead and hope somebody reads it.
            # TODO: logging
            print(f'Clientid {clientid} not found in table {ClientInfo.__tablename__}.')
            return

        doctable = DOCTYPE_TABLE_MAP[doctype]
        docrev = DOCTYPE_DOCREV_MAP[doctype]

        query = local_session.query(doctable).filter_by(clientid=clientid, revision=docrev)
        query = query.order_by(doctable.idx.desc())
        doc = query.first()

        if not doc:
            print(f'Clientid {clientid} not found in table {doctable.__tablename__}.')
            return

        if doc.pdf_path:
            # PDF already exists, won't save again
            return

        ### Read HTML page
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

        ### Generate PDF document
        pdf = HTML(string=html).write_pdf(stylesheets=[css])
        pdf_hash = hashlib.sha1(pdf).hexdigest()

        clientid = int(clientid)

        filename = f'ModoBio_{doctype.name}_v{doc.revision}_client{clientid:05d}_{doc.signdate}.pdf'
        bucket_name = current_app.config['DOCS_BUCKET_NAME']

        if current_app.config['DOCS_STORE_LOCAL']:
            path = pathlib.Path(bucket_name)
            path.mkdir(parents=True, exist_ok=True)

            fullname = path / filename

            with open(fullname, mode='wb') as fh:
                fh.write(pdf)

            pdf_path = fullname.as_posix()
        else:
            pdf_obj = io.BytesIO(pdf)
            pdf_path = f'id{clientid:05d}/{filename}'

            s3 = boto3.client('s3')
            s3.upload_fileobj(pdf_obj, bucket_name, pdf_path)

        doc.pdf_path = pdf_path
        doc.pdf_hash = pdf_hash
        local_session.commit()
        local_session.remove()

        if current_app.config['DEBUG']:
            print('PDF stored at:', pdf_path)

def merge_pdfs(documents: list, clientid: int) -> str:
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
    bucket_name = current_app.config['DOCS_BUCKET_NAME']

    merger = PdfFileMerger()
    bufs = []
    if current_app.config['DOCS_STORE_LOCAL']:
        for doc in documents:
            try:
                merger.append(doc)
            except FileNotFoundError:
                # Temporary file may have changed or disappeared if flask was restarted
                pass
    else:
        s3 = boto3.client('s3')
        for doc in documents:
            doc_buf = io.BytesIO()
            s3.download_fileobj(bucket_name, doc, doc_buf)
            doc_buf.seek(0)
            bufs.append(doc_buf)
            merger.append(doc_buf)

    pdf_buf = io.BytesIO()
    merger.write(pdf_buf)
    merger.close()
    for buf in bufs:
        buf.close()
    pdf_buf.seek(0)

    clientid = int(clientid)
    signdate = date.today().isoformat()
    filename = f'ModoBio_client{clientid:05d}_{signdate}.pdf'

    if current_app.config['DOCS_STORE_LOCAL']:
        path = pathlib.Path(bucket_name)
        path.mkdir(parents=True, exist_ok=True)

        fullname = path / filename

        with open(fullname, mode='wb') as fh:
            fh.write(pdf_buf.read())

        pdf_path = fullname.as_posix()
    else:
        # Anything with a 'temp/' prefix in this bucket is set to be deleted after 1 day.
        fullname = f'temp/{filename}'

        s3 = boto3.client('s3')
        s3.upload_fileobj(pdf_buf, bucket_name, fullname)

        params = {
            'Bucket': bucket_name,
            'Key': fullname
        }
        pdf_path = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=600)

    return pdf_path
