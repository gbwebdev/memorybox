"""Memorybox
  Reveal a new memory picture everyday
  (through a simple webapp and/or by
  printing it on a peripage thermal printer).
"""
import logging
import os
import sys
import click

from flask import Flask, current_app, g
from flask.cli import FlaskGroup, with_appcontext, pass_script_info
from flask_socketio import SocketIO

from memorybox.config import Config
from memorybox.login import login_manager


logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper())
logger = logging.getLogger("memorybox")

socketio = SocketIO()

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
        SQLALCHEMY_DATABASE_URI='sqlite:///memorybox.db',
        ALLOWED_HOSTS=['127.0.0.1', 'localhost'],
        REQUIRE_HTTPS=False,
        REMEMBER_COOKIE_DURATION=30*24*3600,
        REMEMBER_COOKIE_SECURE=True,
        BAN_FINDTIME = 900,
        BANTIME=1800
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
        login_manager.init_app(app)
        login_manager.login_view = "auth.login"
        socketio.init_app(app)
        logger.debug("Init app done")
    
    from memorybox import blueprints
    app.register_blueprint(blueprints.main.bp)
    app.register_blueprint(blueprints.auth.bp)

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
@click.option('-m',
              '--mode',
              type=click.Choice(['dev', 'prod'], case_sensitive=False,),
              default="prod",
              help="Mode")
@pass_script_info
def cli(script_info, mode):
    """Management script for the Wiki application."""
    script_info.mode = mode

@cli.command()
@with_appcontext
def fetch_memories():
    """Retreive memories from external source"""
    logger.info("Fetching memories")
    from memorybox.tools.fetch_memories import fetch_memories as fetch_memories_func
    fetch_memories_func()

@cli.command()
@click.option("-r",
              "--reset",
              is_flag=True,
              show_default=True,
              default=False,
              help="Reset the database.")
@with_appcontext
def init_db(reset):
    """Initialize the databse"""
    logger.info("Initializing database")
    from memorybox.tools import init_db
    with current_app.app_context():
        init_db.init_db(reset)

@cli.command()
def run_dev():
    """Run in dev mode"""
    app = create_app(mode=mode)
    socketio = SocketIO(app)
    socketio.run(app)
