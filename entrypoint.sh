#!/bin/bash

source /home/memorybox/venv/bin/activate
#gunicorn -w $GUNICORN_WORKERS memorybox.wsgi:app --bind 0.0.0.0:$GUNICORN_PORT --log-level $LOG_LEVEL
gunicorn \
  -w $GUNICORN_WORKERS \
  -k eventlet   \
  --bind 0.0.0.0:$GUNICORN_PORT \
  --log-level $LOG_LEVEL \
  --timeout $GUNICORN_TIMEOUT \
  memorybox.wsgi:app
