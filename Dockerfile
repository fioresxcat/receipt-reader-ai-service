FROM python:3.10.12-slim-bullseye

RUN apt-get update -y && apt-get install libgtk2.0-dev -y

RUN pip install --upgrade pip
RUN mkdir -p /ocr/logs

COPY requirements.txt /ocr
WORKDIR /ocr
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir Pillow
RUN pip cache purge

COPY . /ocr
RUN rm -rf /root/.cache/*
# RUN mv /ocr/bpemb /root/.cache

VOLUME "/ocr/logs"

ENTRYPOINT ./run_server.sh
