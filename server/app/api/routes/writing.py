from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.user import User
from app.models.writing import Essay, EssayPrompt
from app.api.schemas.writing import (
    EssayPromptResponse,
    EssaySubmission,
    EssayResponse,
    EssaySummary,
    WritingStats,
    EssayScores,
    EssayFeedback
)
from app.services.auth import get_current_active_user
from app.services.writing_service import WritingService

router = APIRouter(prefix="/writing", tags=["Writing Coach"])


@router.get("/prompts", response_model=List[EssayPromptResponse])
async def get_essay_prompts(
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all essay prompts, optionally filtered by difficulty"""
    prompts = WritingService.get_essay_prompts(db, difficulty)
    return prompts


@router.get("/prompts/{prompt_id}", response_model=EssayPromptResponse)
async def get_essay_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific essay prompt"""
    prompt = WritingService.get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Essay prompt not found"
        )
    return prompt


@router.post("/submit", response_model=EssayResponse, status_code=status.HTTP_201_CREATED)
async def submit_essay(
    submission: EssaySubmission,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit an essay and receive AI feedback"""
    try:
        essay, newly_earned_badges = WritingService.submit_essay(
            db,
            current_user.id,
            submission.prompt_id,
            submission.content,
            submission.parent_essay_id
        )

        # Get prompt details
        prompt = essay.prompt

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

        # Build response
        return EssayResponse(
            id=essay.id,
            prompt_id=essay.prompt_id,
            prompt_title=prompt.title if prompt else None,
            prompt_text=prompt.prompt_text if prompt else None,
            content=essay.content,
            word_count=essay.word_count,
            scores=EssayScores(
                task_response_score=float(essay.task_response_score),
                coherence_cohesion_score=float(essay.coherence_cohesion_score),
                lexical_resource_score=float(essay.lexical_resource_score),
                grammatical_range_score=float(essay.grammatical_range_score),
                overall_score=float(essay.overall_score)
            ) if essay.overall_score else None,
            feedback=EssayFeedback(**essay.ai_feedback) if essay.ai_feedback else None,
            submission_number=essay.submission_number,
            parent_essay_id=essay.parent_essay_id,
            created_at=essay.created_at,
            has_revisions=False,
            newly_earned_badges=badges_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit essay: {str(e)}"
        )


@router.get("/essays", response_model=List[EssaySummary])
async def get_user_essays(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's essay submissions"""
    essays = WritingService.get_user_essays(db, current_user.id, limit)

    return [
        EssaySummary(
            id=essay.id,
            prompt_title=essay.prompt.title if essay.prompt else "Unknown Prompt",
            word_count=essay.word_count,
            overall_score=float(essay.overall_score) if essay.overall_score else None,
            submission_number=essay.submission_number,
            created_at=essay.created_at
        )
        for essay in essays
    ]


@router.get("/essays/{essay_id}", response_model=EssayResponse)
async def get_essay(
    essay_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific essay with full details"""
    essay = WritingService.get_essay_by_id(db, essay_id, current_user.id)

    if not essay:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Essay not found"
        )

    # Check if there are revisions
    revisions = WritingService.get_essay_revisions(db, essay_id, current_user.id)
    has_revisions = len(revisions) > 0

    return EssayResponse(
        id=essay.id,
        prompt_id=essay.prompt_id,
        prompt_title=essay.prompt.title if essay.prompt else None,
        prompt_text=essay.prompt.prompt_text if essay.prompt else None,
        content=essay.content,
        word_count=essay.word_count,
        scores=EssayScores(
            task_response_score=float(essay.task_response_score),
            coherence_cohesion_score=float(essay.coherence_cohesion_score),
            lexical_resource_score=float(essay.lexical_resource_score),
            grammatical_range_score=float(essay.grammatical_range_score),
            overall_score=float(essay.overall_score)
        ) if essay.overall_score else None,
        feedback=EssayFeedback(**essay.ai_feedback) if essay.ai_feedback else None,
        submission_number=essay.submission_number,
        parent_essay_id=essay.parent_essay_id,
        created_at=essay.created_at,
        has_revisions=has_revisions
    )


@router.get("/essays/{essay_id}/revisions", response_model=List[EssayResponse])
async def get_essay_revisions(
    essay_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all revisions of an essay"""
    revisions = WritingService.get_essay_revisions(db, essay_id, current_user.id)

    return [
        EssayResponse(
            id=rev.id,
            prompt_id=rev.prompt_id,
            prompt_title=rev.prompt.title if rev.prompt else None,
            prompt_text=rev.prompt.prompt_text if rev.prompt else None,
            content=rev.content,
            word_count=rev.word_count,
            scores=EssayScores(
                task_response_score=float(rev.task_response_score),
                coherence_cohesion_score=float(rev.coherence_cohesion_score),
                lexical_resource_score=float(rev.lexical_resource_score),
                grammatical_range_score=float(rev.grammatical_range_score),
                overall_score=float(rev.overall_score)
            ) if rev.overall_score else None,
            feedback=EssayFeedback(**rev.ai_feedback) if rev.ai_feedback else None,
            submission_number=rev.submission_number,
            parent_essay_id=rev.parent_essay_id,
            created_at=rev.created_at,
            has_revisions=False
        )
        for rev in revisions
    ]


@router.get("/stats", response_model=WritingStats)
async def get_writing_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's writing statistics"""
    stats = WritingService.get_user_stats(db, current_user.id)
    return WritingStats(**stats)
