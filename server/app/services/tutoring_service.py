from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime
import hashlib
import json

from app.models.tutoring import (
    TutoringSession,
    TutorProfile,
    SessionReview,
    MilestoneVerification,
    SessionStatus,
    ServiceType
)
from app.models.user import User
from app.api.schemas.tutoring import (
    SessionCreate,
    TutorProfileCreate,
    TutorProfileUpdate,
    ReviewCreate,
    MilestoneVerificationCreate,
    TutorFilters
)

class TutoringService:
    """Service layer for tutoring escrow functionality"""

    @staticmethod
    def create_tutor_profile(db: Session, user_id: int, profile_data: TutorProfileCreate) -> TutorProfile:
        """Create a new tutor profile"""
        # Check if profile already exists
        existing = db.query(TutorProfile).filter(TutorProfile.user_id == user_id).first()
        if existing:
            raise ValueError("Tutor profile already exists")

        profile = TutorProfile(
            user_id=user_id,
            bio=profile_data.bio,
            specializations=json.dumps(profile_data.specializations) if profile_data.specializations else "[]",
            hourly_rate=profile_data.hourly_rate,
            wallet_address=profile_data.wallet_address
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_tutor_profile(db: Session, user_id: int, profile_data: TutorProfileUpdate) -> TutorProfile:
        """Update tutor profile"""
        profile = db.query(TutorProfile).filter(TutorProfile.user_id == user_id).first()
        if not profile:
            raise ValueError("Tutor profile not found")

        if profile_data.bio is not None:
            profile.bio = profile_data.bio
        if profile_data.specializations is not None:
            profile.specializations = json.dumps(profile_data.specializations)
        if profile_data.hourly_rate is not None:
            profile.hourly_rate = profile_data.hourly_rate
        if profile_data.is_available is not None:
            profile.is_available = profile_data.is_available
        if profile_data.availability_schedule is not None:
            profile.availability_schedule = profile_data.availability_schedule

        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_tutor_profile(db: Session, user_id: int) -> Optional[TutorProfile]:
        """Get tutor profile by user ID"""
        return db.query(TutorProfile).filter(TutorProfile.user_id == user_id).first()

    @staticmethod
    def get_available_tutors(db: Session, filters: Optional[TutorFilters] = None, skip: int = 0, limit: int = 20) -> tuple[List[TutorProfile], int]:
        """Get list of available tutors with optional filters"""
        query = db.query(TutorProfile).filter(TutorProfile.is_available == True)

        if filters:
            if filters.min_rating:
                query = query.filter(TutorProfile.average_rating >= filters.min_rating)
            if filters.max_hourly_rate:
                query = query.filter(TutorProfile.hourly_rate <= filters.max_hourly_rate)

        total = query.count()
        tutors = query.order_by(TutorProfile.reputation_badges.desc()).offset(skip).limit(limit).all()

        return tutors, total

    @staticmethod
    def create_session(db: Session, learner_id: int, session_data: SessionCreate) -> TutoringSession:
        """Create a new tutoring session"""
        # Validate tutor exists if specified
        if session_data.tutor_id:
            tutor = db.query(User).filter(User.id == session_data.tutor_id).first()
            if not tutor:
                raise ValueError("Tutor not found")

            if session_data.tutor_id == learner_id:
                raise ValueError("Cannot create session with yourself")

        # Create session
        session = TutoringSession(
            learner_id=learner_id,
            tutor_id=session_data.tutor_id,
            service_type=ServiceType(session_data.service_type),
            title=session_data.title,
            description=session_data.description,
            amount=session_data.amount,
            platform_fee=session_data.amount * 0.05,  # 5% platform fee
            status=SessionStatus.IN_PROGRESS if session_data.tutor_id else SessionStatus.CREATED
        )

        if session_data.tutor_id:
            session.accepted_at = datetime.utcnow()

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def accept_session(db: Session, session_id: int, tutor_id: int) -> TutoringSession:
        """Tutor accepts an open session"""
        session = db.query(TutoringSession).filter(TutoringSession.id == session_id).first()

        if not session:
            raise ValueError("Session not found")
        if session.status != SessionStatus.CREATED:
            raise ValueError("Session is not available for acceptance")
        if session.tutor_id is not None:
            raise ValueError("Session already has a tutor")
        if session.learner_id == tutor_id:
            raise ValueError("Cannot accept your own session")

        session.tutor_id = tutor_id
        session.status = SessionStatus.IN_PROGRESS
        session.accepted_at = datetime.utcnow()

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def submit_session(db: Session, session_id: int, tutor_id: int, submission_notes: Optional[str] = None, submission_url: Optional[str] = None) -> TutoringSession:
        """Tutor submits completed work"""
        session = db.query(TutoringSession).filter(TutoringSession.id == session_id).first()

        if not session:
            raise ValueError("Session not found")
        if session.tutor_id != tutor_id:
            raise ValueError("Not authorized")
        if session.status != SessionStatus.IN_PROGRESS:
            raise ValueError("Session is not in progress")

        session.status = SessionStatus.PENDING_REVIEW
        session.submission_notes = submission_notes
        session.submission_url = submission_url
        session.submitted_at = datetime.utcnow()

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def verify_and_complete_session(
        db: Session,
        session_id: int,
        verifier_id: int,
        verification_data: MilestoneVerificationCreate,
        attestation_signature: str
    ) -> TutoringSession:
        """Platform verifies milestone and completes session"""
        session = db.query(TutoringSession).filter(TutoringSession.id == session_id).first()

        if not session:
            raise ValueError("Session not found")
        if session.status != SessionStatus.PENDING_REVIEW:
            raise ValueError("Session not pending review")

        # Create milestone verification record
        improvement = None
        if verification_data.before_score and verification_data.after_score:
            improvement = ((verification_data.after_score - verification_data.before_score) / verification_data.before_score) * 100

        verification = MilestoneVerification(
            session_id=session_id,
            criteria_type=verification_data.criteria_type,
            criteria_met=True,
            before_score=verification_data.before_score,
            after_score=verification_data.after_score,
            improvement_percentage=improvement,
            evidence_url=verification_data.evidence_url,
            evidence_notes=verification_data.evidence_notes,
            verified_by_id=verifier_id,
            attestation_hash=attestation_signature[:64]  # Store truncated hash
        )

        db.add(verification)

        # Update session
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.verified_by_id = verifier_id
        session.verified_at = datetime.utcnow()
        session.attestation_signature = attestation_signature

        # Update tutor stats
        tutor_profile = db.query(TutorProfile).filter(TutorProfile.user_id == session.tutor_id).first()
        if tutor_profile:
            tutor_profile.completed_sessions += 1
            tutor_profile.total_earnings += (session.amount - session.platform_fee)
            tutor_profile.reputation_badges += 1

            # Update specific badge count
            service_type_map = {
                ServiceType.ESSAY_FEEDBACK: 'essay_feedback_badges',
                ServiceType.SPEAKING_PRACTICE: 'speaking_practice_badges',
                ServiceType.READING_TUTOR: 'reading_tutor_badges',
                ServiceType.WRITING_COACH: 'writing_coach_badges'
            }
            badge_attr = service_type_map.get(session.service_type)
            if badge_attr:
                current_value = getattr(tutor_profile, badge_attr)
                setattr(tutor_profile, badge_attr, current_value + 1)

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def cancel_session(db: Session, session_id: int, user_id: int) -> TutoringSession:
        """Cancel a session (learner only, before tutor accepts)"""
        session = db.query(TutoringSession).filter(TutoringSession.id == session_id).first()

        if not session:
            raise ValueError("Session not found")
        if session.learner_id != user_id:
            raise ValueError("Not authorized")
        if session.status != SessionStatus.CREATED:
            raise ValueError("Cannot cancel session in current state")

        session.status = SessionStatus.CANCELLED
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def raise_dispute(db: Session, session_id: int, user_id: int, reason: str) -> TutoringSession:
        """Raise a dispute for a session"""
        session = db.query(TutoringSession).filter(TutoringSession.id == session_id).first()

        if not session:
            raise ValueError("Session not found")
        if session.learner_id != user_id and session.tutor_id != user_id:
            raise ValueError("Not authorized")
        if session.status not in [SessionStatus.IN_PROGRESS, SessionStatus.PENDING_REVIEW]:
            raise ValueError("Cannot dispute session in current state")

        session.status = SessionStatus.DISPUTED
        session.dispute_reason = reason
        session.dispute_raised_by_id = user_id
        session.dispute_raised_at = datetime.utcnow()

        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def create_review(db: Session, session_id: int, reviewer_id: int, review_data: ReviewCreate) -> SessionReview:
        """Create a review for a completed session"""
        session = db.query(TutoringSession).filter(TutoringSession.id == session_id).first()

        if not session:
            raise ValueError("Session not found")
        if session.status != SessionStatus.COMPLETED:
            raise ValueError("Can only review completed sessions")
        if session.learner_id != reviewer_id:
            raise ValueError("Only learner can review")

        # Check if review already exists
        existing_review = db.query(SessionReview).filter(
            and_(SessionReview.session_id == session_id, SessionReview.reviewer_id == reviewer_id)
        ).first()
        if existing_review:
            raise ValueError("Review already exists")

        review = SessionReview(
            session_id=session_id,
            reviewer_id=reviewer_id,
            rating=review_data.rating,
            comment=review_data.comment
        )

        db.add(review)
        db.commit()

        # Update tutor average rating
        if session.tutor_id:
            tutor_profile = db.query(TutorProfile).filter(TutorProfile.user_id == session.tutor_id).first()
            if tutor_profile:
                avg_rating = db.query(func.avg(SessionReview.rating)).join(TutoringSession).filter(
                    TutoringSession.tutor_id == session.tutor_id
                ).scalar()
                tutor_profile.average_rating = float(avg_rating) if avg_rating else 0.0
                db.commit()

        db.refresh(review)
        return review

    @staticmethod
    def get_user_sessions(db: Session, user_id: int, as_learner: bool = True, status_filter: Optional[SessionStatus] = None) -> List[TutoringSession]:
        """Get sessions for a user (as learner or tutor)"""
        if as_learner:
            query = db.query(TutoringSession).filter(TutoringSession.learner_id == user_id)
        else:
            query = db.query(TutoringSession).filter(TutoringSession.tutor_id == user_id)

        if status_filter:
            query = query.filter(TutoringSession.status == status_filter)

        return query.order_by(TutoringSession.created_at.desc()).all()

    @staticmethod
    def get_session_by_id(db: Session, session_id: int) -> Optional[TutoringSession]:
        """Get session by ID"""
        return db.query(TutoringSession).filter(TutoringSession.id == session_id).first()

    @staticmethod
    def generate_attestation_signature(session_id: int, tutor_address: str, amount: float) -> str:
        """Generate attestation signature (simplified for demo)"""
        # In production, this should use proper cryptographic signing
        data = f"{session_id}:{tutor_address}:{amount}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def get_platform_stats(db: Session) -> dict:
        """Get platform-wide statistics"""
        total_sessions = db.query(TutoringSession).count()
        total_tutors = db.query(TutorProfile).count()
        total_learners = db.query(TutoringSession.learner_id).distinct().count()

        total_volume = db.query(func.sum(TutoringSession.amount)).filter(
            TutoringSession.status == SessionStatus.COMPLETED
        ).scalar() or 0

        avg_price = db.query(func.avg(TutoringSession.amount)).scalar() or 0

        completed = db.query(TutoringSession).filter(TutoringSession.status == SessionStatus.COMPLETED).count()
        completion_rate = (completed / total_sessions * 100) if total_sessions > 0 else 0

        return {
            "total_sessions": total_sessions,
            "total_tutors": total_tutors,
            "total_learners": total_learners,
            "total_volume": float(total_volume),
            "average_session_price": float(avg_price),
            "completion_rate": completion_rate
        }
