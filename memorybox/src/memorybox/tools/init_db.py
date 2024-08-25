from flask import current_app

from memorybox.db import db
from memorybox.model import memory

def init_db():
    with current_app.app_context():
        current_app.logger.debug(current_app.config)
        db.create_all()