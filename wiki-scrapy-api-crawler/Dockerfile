ARG PYVERSION=3.12
ARG RELEASE=slim-bookworm

FROM python:$PYVERSION-$RELEASE

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

WORKDIR /app/src/wiki_api_crawler

CMD ["scrapy", "crawl", "ru_wiki_api_crawler"]
