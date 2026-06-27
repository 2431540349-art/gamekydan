#!/usr/bin/python3
"""ORM wrapper for player answers tracking"""
from sqlalchemy import ForeignKey, String, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from models import Base, BaseModel

class PlayerAnswer(BaseModel, Base):
    """Mapped class for the player_answers table"""
    __tablename__ = "player_answers"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    game_id: Mapped[str] = mapped_column(String(50), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    article_id: Mapped[int] = mapped_column(nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_taken: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
