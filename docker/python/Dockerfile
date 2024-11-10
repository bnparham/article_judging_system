FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/PY/BIN:$PATH"

RUN pip install --upgrade pip

COPY ../../backend/requirements.txt /app/requirements.txt
COPY ../../backend/ /app

RUN pip install -r requirements.txt