from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ServiceTypeEnum(str, Enum):
    ESSAY_FEEDBACK = "essay_feedback"
    SPEAKING_PRACTICE = "speaking_practice"
    READING_TUTOR = "reading_tutor"
    WRITING_COACH = "writing_coach"

class SessionStatusEnum(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

# ========== Tutor Profile Schemas ==========

class TutorProfileCreate(BaseModel):
    bio: Optional[str] = None
    specializations: List[str] = []
    hourly_rate: float = Field(default=0.01, ge=0.001)
    wallet_address: Optional[str] = None

class TutorProfileUpdate(BaseModel):
    bio: Optional[str] = None
    specializations: Optional[List[str]] = None
    hourly_rate: Optional[float] = Field(default=None, ge=0.001)
    is_available: Optional[bool] = None
    availability_schedule: Optional[str] = None

class TutorProfileResponse(BaseModel):
    id: int
    user_id: int
    bio: Optional[str]
    specializations: List[str]
    hourly_rate: float
    is_available: bool
    total_sessions: int
    completed_sessions: int
    average_rating: float
    reputation_badges: int
    essay_feedback_badges: int
    speaking_practice_badges: int
    reading_tutor_badges: int
    writing_coach_badges: int
    wallet_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TutorWithUserInfo(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    bio: Optional[str]
    specializations: List[str]
    hourly_rate: float
    is_available: bool
    completed_sessions: int
    average_rating: float
    reputation_badges: int

# ========== Session Schemas ==========

class SessionCreate(BaseModel):
    tutor_id: Optional[int] = None  # None for open marketplace
    service_type: ServiceTypeEnum
    title: str = Field(..., min_length=10, max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., ge=0.001)

class SessionAccept(BaseModel):
    session_id: int

class SessionSubmit(BaseModel):
    session_id: int
    submission_notes: Optional[str] = None
    submission_url: Optional[str] = None

class SessionComplete(BaseModel):
    session_id: int
    attestation_signature: str
    transaction_hash: Optional[str] = None

class SessionDisputeCreate(BaseModel):
    session_id: int
    reason: str

class SessionDisputeResolve(BaseModel):
    session_id: int
    refund_to_learner: bool
    resolution_notes: str

class SessionResponse(BaseModel):
    id: int
    session_id_onchain: Optional[int]
    learner_id: int
    tutor_id: Optional[int]
    service_type: str
    title: str
    description: Optional[str]
    amount: float
    platform_fee: float
    status: str
    created_at: datetime
    accepted_at: Optional[datetime]
    submitted_at: Optional[datetime]
    completed_at: Optional[datetime]
    transaction_hash: Optional[str]
    submission_notes: Optional[str]
    submission_url: Optional[str]

    class Config:
        from_attributes = True

class SessionWithParticipants(SessionResponse):
    learner_name: str
    tutor_name: Optional[str]
    tutor_rating: Optional[float]
    tutor_badges: Optional[int]

# ========== Review Schemas ==========

class ReviewCreate(BaseModel):
    session_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    session_id: int
    reviewer_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ========== Milestone Verification Schemas ==========

class MilestoneVerificationCreate(BaseModel):
    session_id: int
    criteria_type: str
    before_score: Optional[float] = None
    after_score: Optional[float] = None
    evidence_url: Optional[str] = None
    evidence_notes: Optional[str] = None

class MilestoneVerificationResponse(BaseModel):
    id: int
    session_id: int
    criteria_type: str
    criteria_met: bool
    before_score: Optional[float]
    after_score: Optional[float]
    improvement_percentage: Optional[float]
    verified_at: datetime

    class Config:
        from_attributes = True

# ========== Dashboard Schemas ==========

class TutorDashboard(BaseModel):
    total_sessions: int
    completed_sessions: int
    active_sessions: int
    total_earnings: float
    average_rating: float
    reputation_badges: int
    recent_sessions: List[SessionResponse]

class LearnerDashboard(BaseModel):
    total_sessions: int
    completed_sessions: int
    active_sessions: int
    total_spent: float
    recent_sessions: List[SessionResponse]

# ========== Marketplace Schemas ==========

class TutorFilters(BaseModel):
    service_type: Optional[ServiceTypeEnum] = None
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    max_hourly_rate: Optional[float] = None
    is_available: Optional[bool] = True

class MarketplaceTutorList(BaseModel):
    tutors: List[TutorWithUserInfo]
    total: int

# ========== Statistics Schemas ==========

class PlatformStats(BaseModel):
    total_sessions: int
    total_tutors: int
    total_learners: int
    total_volume: float  # In ETH
    average_session_price: float
    completion_rate: float
