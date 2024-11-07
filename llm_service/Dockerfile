ARG PYVERSION=3.12
ARG RELEASE=slim-bookworm

FROM python:$PYVERSION-$RELEASE

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . /app
ENV PYTHONPATH=/app
CMD ["python", "./src/server.py"]
