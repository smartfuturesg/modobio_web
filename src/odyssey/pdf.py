"""
This module handles the generation and storage of PDF files for signed documents.
"""

import boto3
import io
import pathlib
import threading

from flask import render_template, session, current_app, _request_ctx_stack
from flask_wtf import FlaskForm
from weasyprint import HTML, CSS

from odyssey import db
from odyssey.constants import DOCTYPE, DOCTYPE_TABLE_MAP, DOCTYPE_DOCREV_MAP
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
        :class:`odyssey.constants.DOCTYPE`, e.g. `DOCTYPE.consent`

    template : str
        Filename of the Flask template for which a PDF file is requested.
        If template=None, it is assumed that the HTML comes from the React frontend.
        This is not yet supported.

    form : :class:`flask.FlaskForm`
        :class:`flask.Request.form` data needed to fill out the template.
        If :attr:`template` is not None, form *must* also be given and can not be None.

    Raises
    ------
    ValueError
        Raised when :attr:`clientid` does not exist in a database table.
    """
    # The first argument is key: we need to copy the current RequestContext and
    # pass it to the thread to ensure that the other thread has the same information
    # as the calling thread. Calling the RequestContext in a 'with' statement,
    # also sets the AppContext, which in turn sets current_app to the right value.
    #
    # However, we cannot just pass the RequestContext, it must be a copy. The
    # main thread keeps working and tries to delete the RequestContext when it
    # is finished, while the pdf thread is still running. This leads to
    # AssertionError: popped wrong app context <x> in stead of <y>.
    thread = threading.Thread(target=_to_pdf,
                              args=(_request_ctx_stack.top.copy(),
                                    clientid, doctype),
                              kwargs={'template': template, 'form': form})
    thread.start()

def _to_pdf(req_ctx, clientid: int, doctype: DOCTYPE, template: str=None, form: FlaskForm=None):
    """ Generate and store a PDF file from a signed document.

    Don't call this function directly, use :func:`to_pdf` for non-blocking,
    multi-threaded operation.
    """
    with req_ctx:
        client = ClientInfo.query.filter_by(clientid=clientid).one_or_none()
        if not client:
            raise ValueError('Clientid {clientid} not found in table {ClientInfo.__tablename__}.')

        doctable = DOCTYPE_TABLE_MAP[doctype]
        docrev = DOCTYPE_DOCREV_MAP[doctype]

        query = doctable.query.filter_by(clientid=clientid, revision=docrev)
        doc = query.one_or_none()

        if not doc:
            raise ValueError('Clientid {clientid} not found in table {doctable.__tablename__}.')

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
        bucket_name = current_app.config['DOCS_BUCKET_NAME']

        if current_app.config['DOCS_STORE_LOCAL']:
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

        query.update({'url': url})
        db.session.commit()

        if current_app.config['DEBUG']:
            print('PDF stored at:', url)
