from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal


class EssayPromptBase(BaseModel):
    title: str
    prompt_text: str
    essay_type: str
    difficulty: str
    word_count_min: int = 200
    word_count_max: int = 300
    time_limit_minutes: int = 40


class EssayPromptResponse(EssayPromptBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EssaySubmission(BaseModel):
    prompt_id: int
    content: str
    parent_essay_id: Optional[int] = None  # For revisions


class EssayFeedback(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    task_response: str
    coherence_cohesion: str
    lexical_resource: str
    grammatical_range: str
    suggestions: List[str]
    revised_outline: str


class EssayScores(BaseModel):
    task_response_score: float
    coherence_cohesion_score: float
    lexical_resource_score: float
    grammatical_range_score: float
    overall_score: float


class EssayResponse(BaseModel):
    id: int
    prompt_id: Optional[int]
    prompt_title: Optional[str]
    prompt_text: Optional[str]
    content: str
    word_count: int
    scores: Optional[EssayScores]
    feedback: Optional[EssayFeedback]
    submission_number: int
    parent_essay_id: Optional[int]
    created_at: datetime
    has_revisions: bool = False
    newly_earned_badges: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class EssaySummary(BaseModel):
    id: int
    prompt_title: Optional[str]
    word_count: int
    overall_score: Optional[float]
    submission_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class WritingStats(BaseModel):
    total_essays: int
    average_score: float
    best_score: float
    total_revisions: int
    average_word_count: int
    score_trends: List[Dict[str, Any]]  # Historical scores
    skill_averages: Dict[str, float]  # Average by rubric criterion
