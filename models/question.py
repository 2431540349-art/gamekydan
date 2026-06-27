#!/usr/bin/python3
"""ORM wrapper for question objects"""
from sqlalchemy import JSON, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from models import Base, BaseModel
from models.engine.sql import session


class Question(BaseModel, Base):
    """Mapped class for the questions table"""

    __tablename__ = "questions"
    content: Mapped[str] = mapped_column(String(1024), nullable=False)
    option_a: Mapped[str] = mapped_column(String(512), nullable=False)
    option_b: Mapped[str] = mapped_column(String(512), nullable=False)
    option_c: Mapped[str] = mapped_column(String(512), nullable=False)
    option_d: Mapped[str] = mapped_column(String(512), nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(10), nullable=False)
    explanation: Mapped[str] = mapped_column(String(2048), nullable=False, default='')
    article_id: Mapped[int] = mapped_column(nullable=False, default=0)
    article_name: Mapped[str] = mapped_column(String(256), nullable=False, default='')
    difficulty: Mapped[str] = mapped_column(String(20), default='medium')
    category: Mapped[str] = mapped_column(String(64), default='general')
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    total_tries: Mapped[int] = mapped_column(default=0)
    right_tries: Mapped[int] = mapped_column(default=0)

    @property
    def points(self):
        """points based on difficulty multiplier"""
        multiplier = 1.0 if self.difficulty == 'easy' else (1.5 if self.difficulty == 'medium' else 2.0)
        return int(100 * multiplier)

    @points.setter
    def points(self, value):
        """dummy setter for backward compatibility on initialization"""
        pass

    @property
    def answers(self):
        """for backward compatibility with original templates/js"""
        return [self.option_a, self.option_b, self.option_c, self.option_d]

    @answers.setter
    def answers(self, value):
        """setter for backward compatibility with list-based answers initialization"""
        if isinstance(value, list) and len(value) >= 2:
            self.option_a = value[0]
            self.option_b = value[1]
            self.option_c = value[2] if len(value) > 2 else ""
            self.option_d = value[3] if len(value) > 3 else ""
            
            # If a temporary right answer text was stored, resolve it to a letter now
            if hasattr(self, '_temp_right_answer') and self._temp_right_answer:
                self.right_answer = self._temp_right_answer

    @property
    def question(self):
        """for backward compatibility with original code"""
        return self.content

    @question.setter
    def question(self, value):
        """setter for backward compatibility"""
        self.content = value

    @property
    def right_answer(self):
        """for backward compatibility with original code"""
        return self.correct_answer

    @right_answer.setter
    def right_answer(self, value):
        """setter for backward compatibility"""
        val_clean = value.strip().lower()
        # Check if it matches any option value to set the letter code
        matched = False
        for letter, opt_val in [('a', self.option_a), ('b', self.option_b), ('c', self.option_c), ('d', self.option_d)]:
            if opt_val and opt_val.strip().lower() == val_clean:
                self.correct_answer = letter
                matched = True
                break
        
        if not matched:
            self.correct_answer = value
            self._temp_right_answer = value

    def answer(self, value, scale=1.0):
        """check if a value is the correct answer"""
        self.total_tries += 1
        is_correct = False
        val_clean = value.strip().lower()
        correct_clean = self.correct_answer.strip().lower()
        
        if val_clean == correct_clean:
            is_correct = True
        elif correct_clean in ['a', 'b', 'c', 'd']:
            if val_clean in ['a', 'b', 'c', 'd']:
                is_correct = (correct_clean == val_clean)
            else:
                correct_text = getattr(self, f"option_{correct_clean}", "")
                if correct_text and correct_text.strip().lower() == val_clean:
                    is_correct = True

        if is_correct:
            self.right_tries += 1
            session.merge(self)
            session.commit()
            return int(self.points * scale)
        return 0

    @classmethod
    def random(cls, category_id=None):
        """get a random question."""
        from sqlalchemy import func
        q = session.query(Question)
        if category_id and category_id != 0:
            q = q.filter(Question.category_id == category_id)
        q = q.order_by(func.random())
        return q.first()

