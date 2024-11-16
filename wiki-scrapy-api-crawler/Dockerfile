ARG PYVERSION=3.12
ARG RELEASE=slim-bookworm

FROM python:$PYVERSION-$RELEASE

WORKDIR /app

RUN groupadd -r web && useradd -d /app -r -g web web \
    && chown web:web -R /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

WORKDIR /app/src/wiki_api_crawler

USER web

CMD ["scrapy", "crawl", "wiki_api_crawler"]
