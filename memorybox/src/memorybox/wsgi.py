import logging
from os import getenv
from werkzeug.middleware.proxy_fix import ProxyFix
from memorybox import create_app

PROXY_X_FOR=int(getenv('PROXY_X_FOR', '0'))
PROXY_X_PROTO=int(getenv('PROXY_X_PROTO', '0'))
PROXY_X_HOST=int(getenv('PROXY_X_HOST', '0'))
PROXY_X_PREFIX=int(getenv('PROXY_X_PREFIX', '0'))

app = create_app(mode="prod")

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=PROXY_X_FOR,
    x_proto=PROXY_X_PROTO,
    x_host=PROXY_X_HOST,
    x_prefix=PROXY_X_PREFIX
)