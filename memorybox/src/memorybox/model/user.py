from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from flask_login import UserMixin

from datetime import date
from memorybox.db import db

class User(UserMixin, db.Model):
    """Model for a "memory" (a picture)"""
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
