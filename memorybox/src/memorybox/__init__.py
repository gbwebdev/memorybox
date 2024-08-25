"""Memorybox
  Reveal a new memory picture everyday
  (through a simple webapp and/or by
  printing it on a peripage thermal printer).
"""
import logging
import os
import sys
import click

from flask import Flask, current_app
from flask.cli import FlaskGroup, with_appcontext, pass_script_info


from memorybox import blueprints
from memorybox.config import Config


logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper())
logger = logging.getLogger("memorybox")

def create_app(*args, **kwargs):
    """Flask application factory"""
    ctx = click.get_current_context(silent=True)
    if ctx:
        script_info = ctx.obj
        mode = script_info.mode.upper()
    elif kwargs.get("mode"):
        mode = kwargs["mode"].upper()

    if mode.startswith('DEV'):
        logger.info("Running in dev mode")
        instance_path = None
    elif mode.startswith('PROD'):
        logger.info("Running in production mode")
        instance_path="/var/www/memorybox"
    else:
        logger.error('Unknown mode "%s"', mode)
        sys.exit(1)

    # create and configure the app
    app = Flask(__name__,
                instance_relative_config=True,
                instance_path=instance_path)
    
    app.logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO').upper())
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///memorybox.db'
    )
    app.config.from_pyfile('config.py', silent=True)

    # ensure the instance folder exists
    app.config['memories_path'] = os.path.join(app.instance_path, 'memories')
    app.config['thumbnails_path'] = os.path.join(app.config['memories_path'], 'thumbs')
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config['memories_path'], exist_ok=True)
        os.makedirs(app.config['thumbnails_path'], exist_ok=True)
    except OSError:
        pass
    
    with app.app_context():
        Config()
        from memorybox.db import db
        db.init_app(app)
        logger.debug("Init app done")

    app.register_blueprint(blueprints.main.bp)

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
@click.option('-m',
              '--mode',
              type=click.Choice(['dev', 'prod'], case_sensitive=False,),
              default="prod")
@pass_script_info
def cli(script_info, mode):
    """Management script for the Wiki application."""
    script_info.mode = mode

@cli.command()
@with_appcontext
def fetch_memories():
    """Retreive memories from external source"""
    logger.info("Fetching memories")
    from memorybox.fetch_memories import fetch_memories as fetch_memories_func
    fetch_memories_func()

@cli.command()
@with_appcontext
def init_db():
    """Initialize the databse"""
    logger.info("Initializing database")
    from memorybox.tools import init_db
    with current_app.app_context():
        init_db.init_db()
    
