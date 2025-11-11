from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models import Base

class MetricType(enum.Enum):
    READING_SCORE = "reading_score"
    WRITING_SCORE = "writing_score"
    SPEAKING_SCORE = "speaking_score"
    OVERALL_SCORE = "overall_score"
    QUEST_COMPLETION = "quest_completion"
    STREAK_DAYS = "streak_days"

class ScholarshipRound(Base):
    __tablename__ = "scholarship_rounds"

    id = Column(Integer, primary_key=True, index=True)
    round_id_onchain = Column(Integer, nullable=True, unique=True, index=True)

    # Round details
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    matching_pool = Column(Float, nullable=False)  # In ETH
    total_donations = Column(Float, default=0.0)
    total_distributed = Column(Float, default=0.0)

    # Status
    is_active = Column(Boolean, default=True)
    is_finalized = Column(Boolean, default=False)
    finalized_at = Column(DateTime, nullable=True)

    # Stats
    learner_count = Column(Integer, default=0)
    donor_count = Column(Integer, default=0)
    claim_count = Column(Integer, default=0)

    # Blockchain
    creation_tx_hash = Column(String(100), nullable=True)
    finalization_tx_hash = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    donations = relationship("Donation", back_populates="round", cascade="all, delete-orphan")
    claims = relationship("ImprovementClaim", back_populates="round", cascade="all, delete-orphan")

class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("scholarship_rounds.id"), nullable=False)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Donation details
    amount = Column(Float, nullable=False)  # In ETH
    transaction_hash = Column(String(100), nullable=True)

    # Timestamps
    donated_at = Column(DateTime, default=datetime.utcnow)

    # Anonymous donation option
    is_anonymous = Column(Boolean, default=False)

    # Relationships
    round = relationship("ScholarshipRound", back_populates="donations")
    donor = relationship("User", backref="donations")

class ImprovementClaim(Base):
    __tablename__ = "improvement_claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_id_onchain = Column(Integer, nullable=True, index=True)

    round_id = Column(Integer, ForeignKey("scholarship_rounds.id"), nullable=False)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Improvement metrics
    metric_type = Column(Enum(MetricType), nullable=False)
    before_score = Column(Float, nullable=False)
    after_score = Column(Float, nullable=False)
    improvement_percent = Column(Float, nullable=False)
    timeframe_days = Column(Integer, nullable=False)  # Days of improvement period

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    attestation_signature = Column(Text, nullable=True)

    # Evidence
    evidence_notes = Column(Text, nullable=True)
    evidence_urls = Column(Text, nullable=True)  # JSON string of URLs

    # Reward
    is_rewarded = Column(Boolean, default=False)
    reward_amount = Column(Float, default=0.0)
    reward_tx_hash = Column(String(100), nullable=True)
    rewarded_at = Column(DateTime, nullable=True)

    # QF calculation
    qf_score = Column(Float, default=0.0)
    donation_count = Column(Integer, default=0)  # Virtual donations for QF

    # Timestamps
    claimed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    round = relationship("ScholarshipRound", back_populates="claims")
    learner = relationship("User", foreign_keys=[learner_id], backref="improvement_claims")
    verified_by = relationship("User", foreign_keys=[verified_by_id])

class LearnerImprovementHistory(Base):
    __tablename__ = "learner_improvement_history"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Metric tracking
    metric_type = Column(Enum(MetricType), nullable=False)
    score = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Context
    activity_type = Column(String(100), nullable=True)  # e.g., "reading_passage", "essay_submission"
    activity_id = Column(Integer, nullable=True)

    # Relationships
    learner = relationship("User", backref="improvement_history")

class ScholarshipStats(Base):
    __tablename__ = "scholarship_stats"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Lifetime stats
    total_rewards_earned = Column(Float, default=0.0)
    total_claims_submitted = Column(Integer, default=0)
    total_claims_verified = Column(Integer, default=0)
    total_claims_rewarded = Column(Integer, default=0)

    # Improvement tracking
    average_improvement_percent = Column(Float, default=0.0)
    best_improvement_percent = Column(Float, default=0.0)
    total_improvement_days = Column(Integer, default=0)

    # Participation
    rounds_participated = Column(Integer, default=0)
    last_claim_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    learner = relationship("User", backref="scholarship_stats")
