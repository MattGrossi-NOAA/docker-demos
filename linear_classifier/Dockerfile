FROM python:3.10-slim

WORKDIR /home/jovyan/model

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt