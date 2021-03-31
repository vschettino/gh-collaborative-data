FROM python:3.9-slim

RUN apt update && apt install -y gcc libmariadb3 libmariadb-dev mariadb-client

WORKDIR workspace

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .
CMD python main.py