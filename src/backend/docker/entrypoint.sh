#!/usr/bin/env sh

PORT=8000
WORKERS=${WORKERS:=2}
CERT_FILE=cert.pem
CERT_KEY=key.pem

uvicorn --host 0.0.0.0 --port $PORT --workers $WORKERS --ssl-keyfile=$CERT_KEY --ssl-certfile=$CERT_FILE app:app
