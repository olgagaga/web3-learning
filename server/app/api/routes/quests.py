from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.user import User
from app.api.schemas.quest import (
    QuestResponse,
    UserQuestProgress,
    QuestAcceptRequest,
    QuestStats,
    UserBadgeResponse,
    AllBadgesResponse,
)
from app.services.auth import get_current_active_user
from app.services.quest_service import QuestService
from app.services.badge_service import BadgeService

router = APIRouter(prefix="/quests", tags=["Quests"])


@router.get("/", response_model=List[QuestResponse])
async def get_all_quests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all active quests"""
    quests = QuestService.get_active_quests(db)
    return quests


@router.get("/my-quests", response_model=List[UserQuestProgress])
async def get_my_quests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all quests for the current user"""
    user_quests = QuestService.get_user_quests(db, current_user.id)
    return user_quests


@router.get("/active", response_model=List[UserQuestProgress])
async def get_active_quests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get active quests for the current user"""
    user_quests = QuestService.get_user_active_quests(db, current_user.id)
    return user_quests


@router.post("/accept", response_model=UserQuestProgress)
async def accept_quest(
    request: QuestAcceptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Accept a quest"""
    try:
        user_quest = QuestService.accept_quest(db, current_user.id, request.quest_id)
        return user_quest
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/stats", response_model=QuestStats)
async def get_quest_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quest statistics for the current user"""
    stats = QuestService.get_quest_stats(db, current_user.id)
    return QuestStats(**stats)


@router.get("/badges", response_model=List[UserBadgeResponse])
async def get_my_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all badges earned by the current user"""
    badges = QuestService.get_user_badges(db, current_user.id)
    return badges


@router.get("/badges/all", response_model=List[AllBadgesResponse])
async def get_all_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all available badges"""
    badges = BadgeService.get_all_badges(db)
    return badges


@router.get("/badges/showcase")
async def get_badge_showcase(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's badge showcase with categories and statistics"""
    showcase = BadgeService.get_user_badge_showcase(db, current_user.id)
    return showcase


@router.get("/badges/{badge_id}/progress")
async def get_badge_progress(
    badge_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's progress toward earning a specific badge"""
    progress = BadgeService.get_badge_progress(db, current_user.id, badge_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )
    return progress


@router.get("/badges/progress/all")
async def get_all_badges_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's progress toward all badges"""
    all_badges = BadgeService.get_all_badges(db)
    progress_data = {}

    for badge in all_badges:
        progress = BadgeService.get_badge_progress(db, current_user.id, badge.id)
        if progress:
            progress_data[badge.id] = progress

    return progress_data
