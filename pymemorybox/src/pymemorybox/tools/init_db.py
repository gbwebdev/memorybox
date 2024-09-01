from flask import current_app

from pymemorybox.db import db
from pymemorybox.model import memory

def init_db(drop=False):
    with current_app.app_context():
        current_app.logger.debug(current_app.config)
        if drop:
            db.drop_all()
        db.create_all()