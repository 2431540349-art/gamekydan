#!/usr/bin/python3
"""ORM wrapper for badge definitions"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models import Base, BaseModel

class BadgeDefinition(BaseModel, Base):
    """Mapped class for the badges_definitions table"""
    __tablename__ = "badges_definitions"

    badge_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)
    condition: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
