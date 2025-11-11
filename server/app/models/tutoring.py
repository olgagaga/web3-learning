from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models import Base

class SessionStatus(enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class ServiceType(enum.Enum):
    ESSAY_FEEDBACK = "essay_feedback"
    SPEAKING_PRACTICE = "speaking_practice"
    READING_TUTOR = "reading_tutor"
    WRITING_COACH = "writing_coach"

class TutoringSession(Base):
    __tablename__ = "tutoring_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id_onchain = Column(Integer, nullable=True, index=True)  # Blockchain session ID

    # Participants
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Session details
    service_type = Column(Enum(ServiceType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Financial
    amount = Column(Float, nullable=False)  # In ETH
    platform_fee = Column(Float, default=0.0)

    # Status and timestamps
    status = Column(Enum(SessionStatus), default=SessionStatus.CREATED)
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Blockchain data
    transaction_hash = Column(String(100), nullable=True)
    escrow_address = Column(String(100), nullable=True)

    # Delivery and verification
    submission_notes = Column(Text, nullable=True)
    submission_url = Column(String(500), nullable=True)

    # Attestation
    attestation_signature = Column(Text, nullable=True)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Dispute
    dispute_reason = Column(Text, nullable=True)
    dispute_raised_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    dispute_raised_at = Column(DateTime, nullable=True)
    dispute_resolved_at = Column(DateTime, nullable=True)
    dispute_resolution = Column(Text, nullable=True)

    # Relationships
    learner = relationship("User", foreign_keys=[learner_id], backref="learning_sessions")
    tutor = relationship("User", foreign_keys=[tutor_id], backref="tutoring_sessions")
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    dispute_raised_by = relationship("User", foreign_keys=[dispute_raised_by_id])

class TutorProfile(Base):
    __tablename__ = "tutor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Profile info
    bio = Column(Text, nullable=True)
    specializations = Column(String(500), nullable=True)  # JSON string of specializations
    hourly_rate = Column(Float, nullable=False, default=0.01)  # In ETH

    # Availability
    is_available = Column(Boolean, default=True)
    availability_schedule = Column(Text, nullable=True)  # JSON string

    # Stats
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)

    # Reputation
    reputation_badges = Column(Integer, default=0)  # Total SBT count
    essay_feedback_badges = Column(Integer, default=0)
    speaking_practice_badges = Column(Integer, default=0)
    reading_tutor_badges = Column(Integer, default=0)
    writing_coach_badges = Column(Integer, default=0)

    # Blockchain
    wallet_address = Column(String(100), nullable=True)
    sbt_contract_address = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="tutor_profile")

class SessionReview(Base):
    __tablename__ = "session_reviews"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutoring_sessions.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TutoringSession", backref="reviews")
    reviewer = relationship("User", backref="reviews_given")

class MilestoneVerification(Base):
    __tablename__ = "milestone_verifications"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutoring_sessions.id"), nullable=False)

    # Verification criteria
    criteria_type = Column(String(100), nullable=False)  # e.g., "rubric_improvement", "task_completion"
    criteria_met = Column(Boolean, default=False)

    # Rubric scores (for essay feedback)
    before_score = Column(Float, nullable=True)
    after_score = Column(Float, nullable=True)
    improvement_percentage = Column(Float, nullable=True)

    # Evidence
    evidence_url = Column(String(500), nullable=True)
    evidence_notes = Column(Text, nullable=True)

    # Attestation
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_at = Column(DateTime, default=datetime.utcnow)
    attestation_hash = Column(String(100), nullable=True)

    # Relationships
    session = relationship("TutoringSession", backref="milestone_verifications")
    verified_by = relationship("User")
