FROM python:3.13

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/PY/BIN:$PATH"

# Install required packages and Persian locale
RUN apt-get update && \
    apt-get install -y locales locales-all && \
    echo "fa_IR.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen fa_IR.UTF-8 && \
    update-locale LANG=fa_IR.UTF-8

# Set environment variables for locale
ENV LC_ALL=fa_IR.UTF-8
ENV LANG=fa_IR.UTF-8
ENV LANGUAGE=fa_IR.UTF-8

RUN pip install --upgrade pip

COPY ../../backend/requirements.txt /app/requirements.txt
COPY ../../backend/ /app

RUN pip install -r requirements.txt