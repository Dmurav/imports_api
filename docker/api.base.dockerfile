FROM python:3.7.4-stretch

WORKDIR /
COPY Pipfile Pipfile.lock /
RUN apt-get update && \
    apt-get install -y python-dev libpq-dev && \
    pip install pipenv && \
    pipenv install --deploy --system
