#!/bin/bash

source /home/memorybox/venv/bin/activate

if [ "$RUN_MODE" = "prod" ]; then
  gunicorn \
    -w $GUNICORN_WORKERS \
    -k eventlet   \
    --bind 0.0.0.0:$GUNICORN_PORT \
    --log-level $LOG_LEVEL \
    --timeout $GUNICORN_TIMEOUT \
    --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
    pymemorybox.wsgi:app
else
  pip install -e ./pymemorybox
  python3 -m pymemorybox
fi