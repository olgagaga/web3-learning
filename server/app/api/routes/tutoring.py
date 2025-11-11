from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.tutoring import SessionStatus
from app.services.tutoring_service import TutoringService
from app.api.schemas.tutoring import (
    TutorProfileCreate,
    TutorProfileUpdate,
    TutorProfileResponse,
    TutorWithUserInfo,
    SessionCreate,
    SessionResponse,
    SessionWithParticipants,
    SessionSubmit,
    SessionComplete,
    SessionDisputeCreate,
    ReviewCreate,
    ReviewResponse,
    MilestoneVerificationCreate,
    MilestoneVerificationResponse,
    TutorDashboard,
    LearnerDashboard,
    TutorFilters,
    MarketplaceTutorList,
    PlatformStats
)

router = APIRouter()

# ============ Tutor Profile Endpoints ============

@router.post("/profile", response_model=TutorProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_tutor_profile(
    profile_data: TutorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a tutor profile"""
    try:
        profile = TutoringService.create_tutor_profile(db, current_user.id, profile_data)

        # Parse specializations from JSON
        specializations = json.loads(profile.specializations) if profile.specializations else []

        return TutorProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            bio=profile.bio,
            specializations=specializations,
            hourly_rate=profile.hourly_rate,
            is_available=profile.is_available,
            total_sessions=profile.total_sessions,
            completed_sessions=profile.completed_sessions,
            average_rating=profile.average_rating,
            reputation_badges=profile.reputation_badges,
            essay_feedback_badges=profile.essay_feedback_badges,
            speaking_practice_badges=profile.speaking_practice_badges,
            reading_tutor_badges=profile.reading_tutor_badges,
            writing_coach_badges=profile.writing_coach_badges,
            wallet_address=profile.wallet_address,
            created_at=profile.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/profile", response_model=TutorProfileResponse)
async def update_tutor_profile(
    profile_data: TutorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tutor profile"""
    try:
        profile = TutoringService.update_tutor_profile(db, current_user.id, profile_data)

        specializations = json.loads(profile.specializations) if profile.specializations else []

        return TutorProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            bio=profile.bio,
            specializations=specializations,
            hourly_rate=profile.hourly_rate,
            is_available=profile.is_available,
            total_sessions=profile.total_sessions,
            completed_sessions=profile.completed_sessions,
            average_rating=profile.average_rating,
            reputation_badges=profile.reputation_badges,
            essay_feedback_badges=profile.essay_feedback_badges,
            speaking_practice_badges=profile.speaking_practice_badges,
            reading_tutor_badges=profile.reading_tutor_badges,
            writing_coach_badges=profile.writing_coach_badges,
            wallet_address=profile.wallet_address,
            created_at=profile.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/profile/me", response_model=TutorProfileResponse)
async def get_my_tutor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's tutor profile"""
    profile = TutoringService.get_tutor_profile(db, current_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Tutor profile not found")

    specializations = json.loads(profile.specializations) if profile.specializations else []

    return TutorProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        specializations=specializations,
        hourly_rate=profile.hourly_rate,
        is_available=profile.is_available,
        total_sessions=profile.total_sessions,
        completed_sessions=profile.completed_sessions,
        average_rating=profile.average_rating,
        reputation_badges=profile.reputation_badges,
        essay_feedback_badges=profile.essay_feedback_badges,
        speaking_practice_badges=profile.speaking_practice_badges,
        reading_tutor_badges=profile.reading_tutor_badges,
        writing_coach_badges=profile.writing_coach_badges,
        wallet_address=profile.wallet_address,
        created_at=profile.created_at
    )

@router.get("/marketplace", response_model=MarketplaceTutorList)
async def get_marketplace_tutors(
    skip: int = 0,
    limit: int = 20,
    service_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_hourly_rate: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available tutors in marketplace"""
    filters = TutorFilters(
        service_type=service_type,
        min_rating=min_rating,
        max_hourly_rate=max_hourly_rate,
        is_available=True
    )

    profiles, total = TutoringService.get_available_tutors(db, filters, skip, limit)

    tutors_with_info = []
    for profile in profiles:
        user = db.query(User).filter(User.id == profile.user_id).first()
        if user:
            specializations = json.loads(profile.specializations) if profile.specializations else []

            tutors_with_info.append(TutorWithUserInfo(
                id=profile.id,
                user_id=profile.user_id,
                name=user.name,
                email=user.email,
                bio=profile.bio,
                specializations=specializations,
                hourly_rate=profile.hourly_rate,
                is_available=profile.is_available,
                completed_sessions=profile.completed_sessions,
                average_rating=profile.average_rating,
                reputation_badges=profile.reputation_badges
            ))

    return MarketplaceTutorList(tutors=tutors_with_info, total=total)

# ============ Session Endpoints ============

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tutoring session"""
    try:
        session = TutoringService.create_session(db, current_user.id, session_data)

        return SessionResponse(
            id=session.id,
            session_id_onchain=session.session_id_onchain,
            learner_id=session.learner_id,
            tutor_id=session.tutor_id,
            service_type=session.service_type.value,
            title=session.title,
            description=session.description,
            amount=session.amount,
            platform_fee=session.platform_fee,
            status=session.status.value,
            created_at=session.created_at,
            accepted_at=session.accepted_at,
            submitted_at=session.submitted_at,
            completed_at=session.completed_at,
            transaction_hash=session.transaction_hash,
            submission_notes=session.submission_notes,
            submission_url=session.submission_url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/accept", response_model=SessionResponse)
async def accept_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept a tutoring session"""
    try:
        session = TutoringService.accept_session(db, session_id, current_user.id)

        return SessionResponse(
            id=session.id,
            session_id_onchain=session.session_id_onchain,
            learner_id=session.learner_id,
            tutor_id=session.tutor_id,
            service_type=session.service_type.value,
            title=session.title,
            description=session.description,
            amount=session.amount,
            platform_fee=session.platform_fee,
            status=session.status.value,
            created_at=session.created_at,
            accepted_at=session.accepted_at,
            submitted_at=session.submitted_at,
            completed_at=session.completed_at,
            transaction_hash=session.transaction_hash,
            submission_notes=session.submission_notes,
            submission_url=session.submission_url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/submit", response_model=SessionResponse)
async def submit_session(
    session_id: int,
    submit_data: SessionSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit completed work for a session"""
    try:
        session = TutoringService.submit_session(
            db, session_id, current_user.id,
            submit_data.submission_notes,
            submit_data.submission_url
        )

        return SessionResponse(
            id=session.id,
            session_id_onchain=session.session_id_onchain,
            learner_id=session.learner_id,
            tutor_id=session.tutor_id,
            service_type=session.service_type.value,
            title=session.title,
            description=session.description,
            amount=session.amount,
            platform_fee=session.platform_fee,
            status=session.status.value,
            created_at=session.created_at,
            accepted_at=session.accepted_at,
            submitted_at=session.submitted_at,
            completed_at=session.completed_at,
            transaction_hash=session.transaction_hash,
            submission_notes=session.submission_notes,
            submission_url=session.submission_url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: int,
    complete_data: SessionComplete,
    verification_data: MilestoneVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify milestone and complete session (admin/platform only)"""
    # In production, check if user has admin/verifier role
    try:
        session = TutoringService.verify_and_complete_session(
            db, session_id, current_user.id,
            verification_data,
            complete_data.attestation_signature
        )

        return SessionResponse(
            id=session.id,
            session_id_onchain=session.session_id_onchain,
            learner_id=session.learner_id,
            tutor_id=session.tutor_id,
            service_type=session.service_type.value,
            title=session.title,
            description=session.description,
            amount=session.amount,
            platform_fee=session.platform_fee,
            status=session.status.value,
            created_at=session.created_at,
            accepted_at=session.accepted_at,
            submitted_at=session.submitted_at,
            completed_at=session.completed_at,
            transaction_hash=session.transaction_hash,
            submission_notes=session.submission_notes,
            submission_url=session.submission_url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/cancel", response_model=SessionResponse)
async def cancel_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a session"""
    try:
        session = TutoringService.cancel_session(db, session_id, current_user.id)

        return SessionResponse(
            id=session.id,
            session_id_onchain=session.session_id_onchain,
            learner_id=session.learner_id,
            tutor_id=session.tutor_id,
            service_type=session.service_type.value,
            title=session.title,
            description=session.description,
            amount=session.amount,
            platform_fee=session.platform_fee,
            status=session.status.value,
            created_at=session.created_at,
            accepted_at=session.accepted_at,
            submitted_at=session.submitted_at,
            completed_at=session.completed_at,
            transaction_hash=session.transaction_hash,
            submission_notes=session.submission_notes,
            submission_url=session.submission_url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/dispute", response_model=SessionResponse)
async def raise_dispute(
    session_id: int,
    dispute_data: SessionDisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Raise a dispute for a session"""
    try:
        session = TutoringService.raise_dispute(db, session_id, current_user.id, dispute_data.reason)

        return SessionResponse(
            id=session.id,
            session_id_onchain=session.session_id_onchain,
            learner_id=session.learner_id,
            tutor_id=session.tutor_id,
            service_type=session.service_type.value,
            title=session.title,
            description=session.description,
            amount=session.amount,
            platform_fee=session.platform_fee,
            status=session.status.value,
            created_at=session.created_at,
            accepted_at=session.accepted_at,
            submitted_at=session.submitted_at,
            completed_at=session.completed_at,
            transaction_hash=session.transaction_hash,
            submission_notes=session.submission_notes,
            submission_url=session.submission_url
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/my-learner-sessions", response_model=List[SessionResponse])
async def get_my_learner_sessions(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get my sessions as a learner"""
    status_enum = SessionStatus(status_filter) if status_filter else None
    sessions = TutoringService.get_user_sessions(db, current_user.id, as_learner=True, status_filter=status_enum)

    return [SessionResponse(
        id=s.id,
        session_id_onchain=s.session_id_onchain,
        learner_id=s.learner_id,
        tutor_id=s.tutor_id,
        service_type=s.service_type.value,
        title=s.title,
        description=s.description,
        amount=s.amount,
        platform_fee=s.platform_fee,
        status=s.status.value,
        created_at=s.created_at,
        accepted_at=s.accepted_at,
        submitted_at=s.submitted_at,
        completed_at=s.completed_at,
        transaction_hash=s.transaction_hash,
        submission_notes=s.submission_notes,
        submission_url=s.submission_url
    ) for s in sessions]

@router.get("/sessions/my-tutor-sessions", response_model=List[SessionResponse])
async def get_my_tutor_sessions(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get my sessions as a tutor"""
    status_enum = SessionStatus(status_filter) if status_filter else None
    sessions = TutoringService.get_user_sessions(db, current_user.id, as_learner=False, status_filter=status_enum)

    return [SessionResponse(
        id=s.id,
        session_id_onchain=s.session_id_onchain,
        learner_id=s.learner_id,
        tutor_id=s.tutor_id,
        service_type=s.service_type.value,
        title=s.title,
        description=s.description,
        amount=s.amount,
        platform_fee=s.platform_fee,
        status=s.status.value,
        created_at=s.created_at,
        accepted_at=s.accepted_at,
        submitted_at=s.submitted_at,
        completed_at=s.completed_at,
        transaction_hash=s.transaction_hash,
        submission_notes=s.submission_notes,
        submission_url=s.submission_url
    ) for s in sessions]

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get session details"""
    session = TutoringService.get_session_by_id(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check authorization
    if session.learner_id != current_user.id and session.tutor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return SessionResponse(
        id=session.id,
        session_id_onchain=session.session_id_onchain,
        learner_id=session.learner_id,
        tutor_id=session.tutor_id,
        service_type=session.service_type.value,
        title=session.title,
        description=session.description,
        amount=session.amount,
        platform_fee=session.platform_fee,
        status=session.status.value,
        created_at=session.created_at,
        accepted_at=session.accepted_at,
        submitted_at=session.submitted_at,
        completed_at=session.completed_at,
        transaction_hash=session.transaction_hash,
        submission_notes=session.submission_notes,
        submission_url=session.submission_url
    )

# ============ Review Endpoints ============

@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a review for a session"""
    try:
        review = TutoringService.create_review(db, review_data.session_id, current_user.id, review_data)

        return ReviewResponse(
            id=review.id,
            session_id=review.session_id,
            reviewer_id=review.reviewer_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============ Statistics Endpoints ============

@router.get("/stats/platform", response_model=PlatformStats)
async def get_platform_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get platform-wide statistics"""
    stats = TutoringService.get_platform_stats(db)
    return PlatformStats(**stats)
