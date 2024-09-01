from datetime import datetime, timedelta
from sqlalchemy import or_
from flask import current_app

from pymemorybox.db import db
from pymemorybox.model.login_attempt import LoginAttempt

def register_login_attempt(username: str, ipaddress: str, success: bool):
    old_attempts = LoginAttempt.query.filter(LoginAttempt.datetime < datetime.now() - timedelta(seconds=current_app.config['BAN_FINDTIME']) ).all()
    for old_attempt in old_attempts:
        db.session.delete(old_attempt)
    
    if success:
        attempts = LoginAttempt.query.filter(or_(LoginAttempt.username == username, LoginAttempt.ipaddress == ipaddress)).all()
        for attempt in attempts:
            db.session.delete(attempt)
    else:
        login_attempt = LoginAttempt(username=username, ipaddress=ipaddress, datetime=datetime.now())
        db.session.add(login_attempt)
        db.session.commit()

def register_login_attempt(username: str, ipaddress: str):
    login_attempt = LoginAttempt(username=username, ipaddress=ipaddress, datetime=datetime.now())
    db.session.add(login_attempt)
    db.session.commit()
