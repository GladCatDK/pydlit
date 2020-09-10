FROM python:3.7-alpine

COPY requirements.txt /
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev && pip install -r /requirements.txt && apk del .build-deps
COPY app /app
WORKDIR /app
CMD python main.py
EXPOSE 5001
