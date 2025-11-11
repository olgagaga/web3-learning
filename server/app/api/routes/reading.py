from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.user import User
from app.models.reading import ReadingItem, ReadingQuestion
from app.api.schemas.reading import (
    ReadingItemResponse,
    ReadingItemSummary,
    ReadingQuestionResponse,
    AnswerSubmission,
    AnswerFeedback,
    ReadingStats
)
from app.services.auth import get_current_active_user
from app.services.reading_service import ReadingService

router = APIRouter(prefix="/reading", tags=["Reading Practice"])


@router.get("/next", response_model=ReadingItemResponse)
async def get_next_reading_item(
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get next reading item with adaptive difficulty"""
    reading_item = ReadingService.get_next_reading_item(db, current_user.id, difficulty)

    if not reading_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reading items available"
        )

    # Don't include correct answers in the response
    response = ReadingItemResponse.from_orm(reading_item)
    for question in response.questions:
        question.correct_answer = None
        question.explanation = None

    return response


@router.get("/items", response_model=List[ReadingItemSummary])
async def get_reading_items(
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of all reading items"""
    query = db.query(ReadingItem)

    if difficulty:
        query = query.filter(ReadingItem.difficulty == difficulty)

    items = query.all()

    return [
        ReadingItemSummary(
            id=item.id,
            title=item.title,
            difficulty=item.difficulty,
            question_count=len(item.questions),
            skill_tags=item.skill_tags or []
        )
        for item in items
    ]


@router.get("/items/{item_id}", response_model=ReadingItemResponse)
async def get_reading_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific reading item by ID"""
    reading_item = db.query(ReadingItem).filter(ReadingItem.id == item_id).first()

    if not reading_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading item not found"
        )

    # Don't include correct answers
    response = ReadingItemResponse.from_orm(reading_item)
    for question in response.questions:
        question.correct_answer = None
        question.explanation = None

    return response


@router.post("/submit", response_model=AnswerFeedback)
async def submit_answer(
    submission: AnswerSubmission,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit answer to a reading question"""
    result = ReadingService.submit_answer(
        db,
        current_user.id,
        submission.question_id,
        submission.user_answer,
        submission.time_spent_seconds
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    is_correct, question, newly_earned_badges = result

    # Format badges for response
    badges_data = [
        {
            "id": ub.badge.id,
            "name": ub.badge.name,
            "description": ub.badge.description,
            "badge_type": ub.badge.badge_type,
            "icon_url": ub.badge.icon_url,
        }
        for ub in newly_earned_badges
    ]

    return AnswerFeedback(
        question_id=question.id,
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation or "No explanation available",
        skill_category=question.skill_category,
        newly_earned_badges=badges_data
    )


@router.get("/stats", response_model=ReadingStats)
async def get_reading_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's reading practice statistics"""
    stats = ReadingService.get_user_stats(db, current_user.id)
    return ReadingStats(**stats)
