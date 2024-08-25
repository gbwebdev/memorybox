from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from memorybox.db import db

class Memory(db.Model):
    """Model for a "memory" (a picture)"""
    id: Mapped[Integer] = mapped_column(primary_key=True)
    filename: Mapped[String] = mapped_column(unique=True)
    author: Mapped[String]
    release_date: Mapped[DateTime]
    captation: Mapped[String]
    printed: Mapped[Boolean]
