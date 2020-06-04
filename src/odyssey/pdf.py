"""
This module handles the generation and storage of PDFs from templates.
"""

import boto3
import io
import os
import pathlib
import threading

from flask import render_template
from flask_wtf import FlaskForm
from flask_weasyprint import HTML, render_pdf

from odyssey import db, app

def to_pdf(clientid: int, template: str, form: FlaskForm):
    thread = threading.Thread(target=_to_pdf, args=(clientid, template, form))
    thread.start()

def _to_pdf(clientid: int, template: str, form: FlaskForm):
    with app.test_request_context(base_url=''):
        html = render_template(template, form=form, pdf=True)
        pdf = HTML(string=html).write_pdf()

        tname = pathlib.Path(template).stem
        clientid = int(clientid)
        signdate = form.data['signdate'].isoformat()
        # docrev = form.data['docrev']
        docrev = 20200528

        filename = f'ModoBio_{tname}_v{docrev}_client{clientid:05d}_{signdate}.pdf'
        bucket_name = app.config['DOCS_BUCKET_NAME']
        bucket_name += str(clientid)

        if os.getenv('FLASK_ENV') == 'development':
            path = pathlib.Path(bucket_name)
            path.mkdir(parents=True, exist_ok=True)
            print('PDF stored at:', path / filename)
            with open(path / filename, mode='wb') as fh:
                fh.write(pdf)
        else:
            pdf_obj = io.BytesIO(pdf)

            s3 = boto3.client('s3')
            s3.upload_fileobj(pdf_obj, bucket_name, filename)
