"""Memorybox
  Reveal a new memory picture everyday
  (through a simple webapp and/or by
  printing it on a peripage thermal printer).
"""
import logging
import os
import sys
import click
from datetime import datetime


from flask import Flask, current_app, g
from flask.cli import FlaskGroup, with_appcontext, pass_script_info
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from pymemorybox.config import Config
from pymemorybox.login import login_manager


logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper())
logger = logging.getLogger("memorybox")

socketio = SocketIO()
jwt = JWTManager()
scheduler = BackgroundScheduler()

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
    app.config.from_pyfile('config.py')

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
        from pymemorybox.db import db
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = "auth.login"
        socketio.init_app(app)
        jwt.init_app(app)
        logger.debug("Init app done")
    
    from pymemorybox import blueprints
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
    from pymemorybox.tools.fetch_memories import fetch_memories as fetch_memories_func
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
    from pymemorybox.tools import init_db
    with current_app.app_context():
        init_db.init_db(reset)

@cli.command()
@with_appcontext
@click.option('-u',
            '--username',
            required=True,
            type=str,
            help="The user's name.")
@click.option('-p',
            '--password',
            required=True,
            type=str,
            help="The user's password.")
def create_user(username, password):
    """Create a user"""
    logger.info("Creating a user")
    import uuid
    from pymemorybox.model.user import User
    from werkzeug.security import generate_password_hash
    from pymemorybox.db import db
    new_user = User(
                username=username,
                password=generate_password_hash(password),
                uid=str(uuid.uuid4()).strip())
    with current_app.app_context():
        db.session.add(new_user)
        db.session.commit()

@cli.command()
def run_dev():
    """Run in dev mode"""
    logger.info("Running the dev server.")
    app = create_app(mode="dev")
    socketio.run(app)

@cli.command()
@click.option('-s',
            '--server',
            required=True,
            type=str,
            envvar='MEMORYBOX_SERVER',
            help="Memorybox server address.")
@click.option('-t',
            '--token',
            required=True,
            type=str,
            envvar='MEMORYBOX_AGENT_TOKEN',
            help="Token for the agent to authenticate against the server.")
def run_print_agent(server, token):
    """Run the print agent"""
    logger.info("Running the print agent.")
    from pymemorybox.tools import print_agent
    print_agent.run(server, token)


def print_task(app):
    with app.app_context():
        from pymemorybox.blueprints.main import get_memory_by_date, handle_print
        config = Config()

        todays_memory = get_memory_by_date(date.today())

        if datetime.now().strftime("%A") in ["Saturday", "Sunday"] or config.enable_holiday_mode:
            # It is a holiday print day
            if datetime.now().time() >= config.holiday_print_time:
                if not todays_memory.printed:
                    handle_print(todays_memory.id)
        else:
            # It is a workday print day
            if datetime.now().time() >= config.workday_print_time:
                if not todays_memory.printed:
                    handle_print(todays_memory.id)

def setup_print_scheduler(app):
    with app.app_context():
        config = Config()

    scheduler.remove_all_jobs()
    workday_trigger = CronTrigger(hour=config.workday_print_time.hour, minute=config.workday_print_time.minute)
    holiday_trigger = CronTrigger(hour=config.holiday_print_time.hour, minute=config.holiday_print_time.minute)
    scheduler.add_job(print_task, workday_trigger, args=[app])
    scheduler.add_job(print_task, holiday_trigger, args=[app])
    scheduler.start()

def main():
    app = create_app(mode="dev")
    setup_print_scheduler(app)
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
