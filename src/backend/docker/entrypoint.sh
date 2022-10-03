#!/usr/bin/env sh

PORT=8000
WORKERS=${WORKERS:=2}

uvicorn --host 0.0.0.0 --port $PORT --workers $WORKERS --proxy-headers app:app
