from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, ARRAY, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class ReadingItem(Base):
    __tablename__ = "reading_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    passage = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=False)  # easy, medium, hard
    skill_tags = Column(ARRAY(String), default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    questions = relationship("ReadingQuestion", back_populates="reading_item", cascade="all, delete-orphan")


class ReadingQuestion(Base):
    __tablename__ = "reading_questions"

    id = Column(Integer, primary_key=True, index=True)
    reading_item_id = Column(Integer, ForeignKey("reading_items.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer = Column(String(10), nullable=False)  # A, B, C, or D
    explanation = Column(Text)
    skill_category = Column(String(100))  # inference, vocabulary, main-idea, detail, etc.

    # Relationships
    reading_item = relationship("ReadingItem", back_populates="questions")
    attempts = relationship("UserReadingAttempt", back_populates="question", cascade="all, delete-orphan")


class UserReadingAttempt(Base):
    __tablename__ = "user_reading_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("reading_questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(String(10), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent_seconds = Column(Integer)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    question = relationship("ReadingQuestion", back_populates="attempts")
