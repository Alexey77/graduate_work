ARG PYVERSION=3.12
ARG RELEASE=slim-bookworm

FROM python:$PYVERSION-$RELEASE

WORKDIR /app

RUN groupadd -r web && useradd -d /app -r -g web web \
    && chown web:web -R /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . /app

USER web

ENV PYTHONPATH=/app

CMD ["python", "./src/server.py"]
