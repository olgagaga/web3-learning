from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional, Tuple
from app.models.writing import Essay, EssayPrompt
from app.models.user import User
from app.services.gemini_service import GeminiService
from app.services.quest_service import QuestService
from app.services.badge_service import BadgeService
from app.models.quest import UserBadge
from decimal import Decimal


class WritingService:
    @staticmethod
    def get_essay_prompts(db: Session, difficulty: Optional[str] = None) -> List[EssayPrompt]:
        """Get all essay prompts, optionally filtered by difficulty"""
        query = db.query(EssayPrompt)
        if difficulty:
            query = query.filter(EssayPrompt.difficulty == difficulty)
        return query.all()

    @staticmethod
    def get_prompt_by_id(db: Session, prompt_id: int) -> Optional[EssayPrompt]:
        """Get a specific essay prompt"""
        return db.query(EssayPrompt).filter(EssayPrompt.id == prompt_id).first()

    @staticmethod
    def submit_essay(
        db: Session,
        user_id: int,
        prompt_id: int,
        content: str,
        parent_essay_id: Optional[int] = None
    ) -> Tuple[Essay, List[UserBadge]]:
        """Submit an essay and get AI feedback"""

        # Get the prompt
        prompt = WritingService.get_prompt_by_id(db, prompt_id)
        if not prompt:
            raise ValueError("Prompt not found")

        # Count words
        word_count = len(content.split())

        # Determine submission number
        submission_number = 1
        if parent_essay_id:
            parent_essay = db.query(Essay).filter(Essay.id == parent_essay_id).first()
            if parent_essay:
                submission_number = parent_essay.submission_number + 1

        # Get AI feedback
        ai_result = GeminiService.score_essay(content, prompt.prompt_text, word_count)

        # Create essay record
        essay = Essay(
            user_id=user_id,
            prompt_id=prompt_id,
            content=content,
            word_count=word_count,
            task_response_score=Decimal(str(ai_result["task_response_score"])),
            coherence_cohesion_score=Decimal(str(ai_result["coherence_cohesion_score"])),
            lexical_resource_score=Decimal(str(ai_result["lexical_resource_score"])),
            grammatical_range_score=Decimal(str(ai_result["grammatical_range_score"])),
            overall_score=Decimal(str(ai_result["overall_score"])),
            ai_feedback=ai_result["feedback"],
            submission_number=submission_number,
            parent_essay_id=parent_essay_id
        )

        db.add(essay)

        # Update user stats
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.essays_written = (user.essays_written or 0) + 1

        db.commit()
        db.refresh(essay)

        # Update quest progress
        QuestService.update_quest_progress(
            db,
            user_id,
            "essay_complete",
            {"overall_score": float(essay.overall_score)}
        )

        # Check and award badges
        newly_earned_badges = BadgeService.check_and_award_badges(db, user_id)

        return essay, newly_earned_badges

    @staticmethod
    def get_user_essays(db: Session, user_id: int, limit: int = 10) -> List[Essay]:
        """Get user's essays"""
        return (
            db.query(Essay)
            .filter(Essay.user_id == user_id)
            .order_by(desc(Essay.created_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_essay_by_id(db: Session, essay_id: int, user_id: int) -> Optional[Essay]:
        """Get a specific essay"""
        return (
            db.query(Essay)
            .filter(Essay.id == essay_id, Essay.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_essay_revisions(db: Session, essay_id: int, user_id: int) -> List[Essay]:
        """Get all revisions of an essay"""
        return (
            db.query(Essay)
            .filter(Essay.parent_essay_id == essay_id, Essay.user_id == user_id)
            .order_by(Essay.submission_number)
            .all()
        )

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict:
        """Get writing statistics for user"""

        # Total essays
        total_essays = (
            db.query(func.count(Essay.id))
            .filter(Essay.user_id == user_id)
            .scalar() or 0
        )

        if total_essays == 0:
            return {
                "total_essays": 0,
                "average_score": 0,
                "best_score": 0,
                "total_revisions": 0,
                "average_word_count": 0,
                "score_trends": [],
                "skill_averages": {}
            }

        # Average score
        average_score = (
            db.query(func.avg(Essay.overall_score))
            .filter(Essay.user_id == user_id)
            .scalar() or 0
        )

        # Best score
        best_score = (
            db.query(func.max(Essay.overall_score))
            .filter(Essay.user_id == user_id)
            .scalar() or 0
        )

        # Total revisions (essays with submission_number > 1)
        total_revisions = (
            db.query(func.count(Essay.id))
            .filter(Essay.user_id == user_id, Essay.submission_number > 1)
            .scalar() or 0
        )

        # Average word count
        average_word_count = (
            db.query(func.avg(Essay.word_count))
            .filter(Essay.user_id == user_id)
            .scalar() or 0
        )

        # Score trends (recent 10 essays)
        recent_essays = (
            db.query(Essay)
            .filter(Essay.user_id == user_id)
            .order_by(desc(Essay.created_at))
            .limit(10)
            .all()
        )

        score_trends = [
            {
                "date": essay.created_at.isoformat(),
                "overall_score": float(essay.overall_score) if essay.overall_score else 0,
                "submission_number": essay.submission_number
            }
            for essay in reversed(recent_essays)
        ]

        # Skill averages
        skill_averages = {
            "task_response": float(
                db.query(func.avg(Essay.task_response_score))
                .filter(Essay.user_id == user_id)
                .scalar() or 0
            ),
            "coherence_cohesion": float(
                db.query(func.avg(Essay.coherence_cohesion_score))
                .filter(Essay.user_id == user_id)
                .scalar() or 0
            ),
            "lexical_resource": float(
                db.query(func.avg(Essay.lexical_resource_score))
                .filter(Essay.user_id == user_id)
                .scalar() or 0
            ),
            "grammatical_range": float(
                db.query(func.avg(Essay.grammatical_range_score))
                .filter(Essay.user_id == user_id)
                .scalar() or 0
            )
        }

        return {
            "total_essays": total_essays,
            "average_score": round(float(average_score), 2),
            "best_score": round(float(best_score), 2),
            "total_revisions": total_revisions,
            "average_word_count": int(average_word_count),
            "score_trends": score_trends,
            "skill_averages": skill_averages
        }
