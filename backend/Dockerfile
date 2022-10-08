# syntax=docker/dockerfile:1
FROM python:3
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo \
    rustc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
WORKDIR /backend
COPY requirements.txt /backend/
RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install --no-cache-dir -r requirements.txt
COPY . /backend/
