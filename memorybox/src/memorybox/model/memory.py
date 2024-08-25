from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from memorybox.db import db

class Memory(db.Model):
    """Model for a "memory" (a picture)"""
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(unique=True)
    author: Mapped[str]
    release_date: Mapped[datetime]
    captation: Mapped[str]
    printed: Mapped[bool]
