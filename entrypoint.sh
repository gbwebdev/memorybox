#!/bin/bash

source /home/memorybox/venv/bin/activate

if [ "$RUN_MODE" = "prod" ]; then
  #gunicorn -w $GUNICORN_WORKERS memorybox.wsgi:app --bind 0.0.0.0:$GUNICORN_PORT --log-level $LOG_LEVEL
  gunicorn \
    -w $GUNICORN_WORKERS \
    -k eventlet   \
    --bind 0.0.0.0:$GUNICORN_PORT \
    --log-level $LOG_LEVEL \
    --timeout $GUNICORN_TIMEOUT \
    pymemorybox.wsgi:app
else
  pip install -e ./pymemorybox
  python3 -m pymemorybox
fi