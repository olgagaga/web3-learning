from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MetricTypeEnum(str, Enum):
    READING_SCORE = "reading_score"
    WRITING_SCORE = "writing_score"
    SPEAKING_SCORE = "speaking_score"
    OVERALL_SCORE = "overall_score"
    QUEST_COMPLETION = "quest_completion"
    STREAK_DAYS = "streak_days"

# ========== Round Schemas ==========

class RoundCreate(BaseModel):
    duration_days: int = Field(..., ge=1, le=90)
    matching_pool: float = Field(..., ge=0.1)

class RoundResponse(BaseModel):
    id: int
    round_id_onchain: Optional[int]
    start_time: datetime
    end_time: datetime
    matching_pool: float
    total_donations: float
    total_distributed: float
    is_active: bool
    is_finalized: bool
    learner_count: int
    donor_count: int
    claim_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class RoundWithDetails(RoundResponse):
    days_remaining: Optional[int]
    hours_remaining: Optional[int]
    participation_rate: float
    average_improvement: float

# ========== Donation Schemas ==========

class DonationCreate(BaseModel):
    round_id: int
    amount: float = Field(..., ge=0.001)
    is_anonymous: bool = False

class DonationResponse(BaseModel):
    id: int
    round_id: int
    donor_id: int
    donor_name: Optional[str]
    amount: float
    is_anonymous: bool
    donated_at: datetime
    transaction_hash: Optional[str]

    class Config:
        from_attributes = True

# ========== Improvement Claim Schemas ==========

class ClaimCreate(BaseModel):
    round_id: int
    metric_type: MetricTypeEnum
    before_score: float = Field(..., ge=0)
    after_score: float = Field(..., ge=0)
    timeframe_days: int = Field(..., ge=7)
    evidence_notes: Optional[str] = None
    evidence_urls: Optional[List[str]] = []

class ClaimVerify(BaseModel):
    claim_id: int
    is_approved: bool
    notes: Optional[str] = None

class ClaimResponse(BaseModel):
    id: int
    claim_id_onchain: Optional[int]
    round_id: int
    learner_id: int
    learner_name: str
    metric_type: str
    before_score: float
    after_score: float
    improvement_percent: float
    timeframe_days: int
    is_verified: bool
    is_rewarded: bool
    reward_amount: float
    qf_score: float
    claimed_at: datetime
    verified_at: Optional[datetime]

    class Config:
        from_attributes = True

class ClaimWithEvidence(ClaimResponse):
    evidence_notes: Optional[str]
    evidence_urls: List[str]
    verified_by_id: Optional[int]

# ========== Improvement History Schemas ==========

class ImprovementRecordCreate(BaseModel):
    metric_type: MetricTypeEnum
    score: float
    activity_type: Optional[str] = None
    activity_id: Optional[int] = None

class ImprovementRecordResponse(BaseModel):
    id: int
    learner_id: int
    metric_type: str
    score: float
    recorded_at: datetime
    activity_type: Optional[str]

    class Config:
        from_attributes = True

class ImprovementTrend(BaseModel):
    metric_type: str
    data_points: List[dict]  # [{date, score}]
    trend_percent: float
    latest_score: float

# ========== Stats Schemas ==========

class LearnerStatsResponse(BaseModel):
    learner_id: int
    total_rewards_earned: float
    total_claims_submitted: int
    total_claims_verified: int
    total_claims_rewarded: int
    average_improvement_percent: float
    best_improvement_percent: float
    rounds_participated: int

    class Config:
        from_attributes = True

class PlatformStatsResponse(BaseModel):
    total_rounds: int
    active_rounds: int
    total_pool_value: float
    total_distributed: float
    total_learners_rewarded: int
    total_donors: int
    average_donation: float
    total_claims: int
    verified_claims: int
    average_improvement: float

# ========== Dashboard Schemas ==========

class LearnerDashboard(BaseModel):
    current_round: Optional[RoundResponse]
    my_claims: List[ClaimResponse]
    my_stats: LearnerStatsResponse
    improvement_trends: List[ImprovementTrend]
    eligible_for_claim: bool
    estimated_reward: Optional[float]

class DonorDashboard(BaseModel):
    current_round: Optional[RoundResponse]
    my_donations: List[DonationResponse]
    total_donated: float
    learners_supported: int
    impact_score: float

class PublicDashboard(BaseModel):
    current_round: Optional[RoundWithDetails]
    recent_distributions: List[ClaimResponse]
    top_improvers: List[dict]  # [{learner_name, improvement_percent, reward}]
    donation_leaderboard: List[dict]  # [{donor_name, total_donated, is_anonymous}]
    platform_stats: PlatformStatsResponse

# ========== QF Calculation Schemas ==========

class QFAllocation(BaseModel):
    claim_id: int
    learner_address: str
    learner_name: str
    improvement_percent: float
    qf_score: float
    estimated_reward: float
    donation_count: int

class QFRoundSummary(BaseModel):
    round_id: int
    total_pool: float
    total_claims: int
    allocations: List[QFAllocation]

# ========== Finalization Schemas ==========

class RoundFinalize(BaseModel):
    round_id: int
    allocations: List[QFAllocation]
