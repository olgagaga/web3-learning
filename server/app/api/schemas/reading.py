from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime


class QuestionOption(BaseModel):
    A: str
    B: str
    C: str
    D: str


class ReadingQuestionBase(BaseModel):
    question: str
    options: Dict[str, str]
    skill_category: Optional[str] = None


class ReadingQuestionResponse(ReadingQuestionBase):
    id: int
    correct_answer: Optional[str] = None  # Only included after submission
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class ReadingItemBase(BaseModel):
    title: str
    passage: str
    difficulty: str
    skill_tags: List[str] = []


class ReadingItemResponse(ReadingItemBase):
    id: int
    questions: List[ReadingQuestionResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class ReadingItemSummary(BaseModel):
    id: int
    title: str
    difficulty: str
    question_count: int
    skill_tags: List[str]

    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    question_id: int
    user_answer: str
    time_spent_seconds: Optional[int] = None


class AnswerFeedback(BaseModel):
    question_id: int
    is_correct: bool
    correct_answer: str
    explanation: str
    skill_category: Optional[str] = None
    newly_earned_badges: List[Dict[str, Any]] = []


class ReadingStats(BaseModel):
    total_attempts: int
    correct_answers: int
    accuracy: float
    skill_breakdown: Dict[str, Dict[str, Any]]  # skill -> {correct, total, accuracy}
    recent_difficulty: str
    recommended_difficulty: str
