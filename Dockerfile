FROM python:3.9-slim

WORKDIR workspace

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .
# dummy entrypoint so the container will not die
CMD sh -c "top -b >> /dev/null"