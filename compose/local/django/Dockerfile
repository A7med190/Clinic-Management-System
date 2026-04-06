FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements /app/requirements
RUN pip install --upgrade pip && \
    pip install -r requirements/local.txt

COPY . /app/

RUN adduser --disabled-password --no-create-home django_user && \
    chown -R django_user:django_user /app
USER django_user

EXPOSE 8000
