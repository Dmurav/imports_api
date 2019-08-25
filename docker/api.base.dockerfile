FROM python:3.7.4-stretch

WORKDIR /
RUN apt-get update && \
    apt-get install -y python-dev libpq-dev

COPY Pipfile Pipfile.lock /
RUN pip install pipenv && \
    pipenv install --deploy --system

COPY imports/ /project/
