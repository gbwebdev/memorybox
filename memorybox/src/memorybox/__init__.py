"""Memorybox
  Reveal a new memory picture everyday
  (through a simple webapp and/or by
  printing it on a peripage thermal printer).
"""
import logging
import os
import sys

from flask import Flask

from memorybox import db
from memorybox import blueprints

logger = logging.getLogger("baselogger")

def create_app(mode='dev', test_config=None):
    if mode.startswith('dev'):
        instance_path = None
    elif mode.startswith('prod'):
        instance_path="/var/www/memorybox"
    else:
        logger.error('Unknown mode "%s"', mode)
        sys.exit(1)
    # create and configure the app
    app = Flask(__name__,
                instance_relative_config=True,
                instance_path=instance_path)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'memorybox.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    db.init_app(app)

    app.register_blueprint(blueprints.main.bp)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app