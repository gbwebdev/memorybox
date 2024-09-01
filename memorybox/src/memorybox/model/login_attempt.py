from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from memorybox.db import db

class LoginAttempt(db.Model):
    """Model for a login attempt"""
    id: Mapped[int] = mapped_column(primary_key=True)
    datetime: Mapped[datetime]
    username: Mapped[str]
    ipaddress: Mapped[str]
