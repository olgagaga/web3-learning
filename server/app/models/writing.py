from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class EssayPrompt(Base):
    __tablename__ = "essay_prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    prompt_text = Column(Text, nullable=False)
    essay_type = Column(String(50), nullable=False)  # task1, task2, argumentative, etc.
    difficulty = Column(String(50), nullable=False)  # easy, medium, hard
    word_count_min = Column(Integer, default=200)
    word_count_max = Column(Integer, default=300)
    time_limit_minutes = Column(Integer, default=40)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    essays = relationship("Essay", back_populates="prompt")


class Essay(Base):
    __tablename__ = "essays"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prompt_id = Column(Integer, ForeignKey("essay_prompts.id", ondelete="SET NULL"))
    content = Column(Text, nullable=False)
    word_count = Column(Integer)

    # AI scores (IELTS/TOEFL rubric)
    task_response_score = Column(DECIMAL(3, 1))
    coherence_cohesion_score = Column(DECIMAL(3, 1))
    lexical_resource_score = Column(DECIMAL(3, 1))
    grammatical_range_score = Column(DECIMAL(3, 1))
    overall_score = Column(DECIMAL(3, 1))

    # AI feedback
    ai_feedback = Column(JSON)  # Structured feedback from Gemini

    # Revision tracking
    submission_number = Column(Integer, default=1)
    parent_essay_id = Column(Integer, ForeignKey("essays.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    prompt = relationship("EssayPrompt", back_populates="essays")
    revisions = relationship("Essay", remote_side=[parent_essay_id])
