FROM python:3.6

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

RUN apt update
RUN apt install -y libpq-dev python3-dev build-essential libpango-1.0-0 libpangocairo-1.0-0

COPY ./ /usr/src/app
RUN pip install weasyprint
RUN pip install psycopg2
RUN pip install -r requirements.txt

CMD ["flask", "run", "--host", "0.0.0.0"]