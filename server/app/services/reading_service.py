from sqlalchemy.orm import Session
from sqlalchemy import func, and_, Integer
from typing import Optional, Dict, List, Tuple
from app.models.reading import ReadingItem, ReadingQuestion, UserReadingAttempt
from app.models.user import User
from app.services.quest_service import QuestService
from app.services.badge_service import BadgeService
from app.models.quest import UserBadge


class ReadingService:
    @staticmethod
    def get_user_accuracy(db: Session, user_id: int, limit: int = 10) -> float:
        """Calculate user's recent accuracy"""
        recent_attempts = (
            db.query(UserReadingAttempt)
            .filter(UserReadingAttempt.user_id == user_id)
            .order_by(UserReadingAttempt.attempted_at.desc())
            .limit(limit)
            .all()
        )

        if not recent_attempts:
            return 0.5  # Default to 50% if no history

        correct = sum(1 for attempt in recent_attempts if attempt.is_correct)
        return correct / len(recent_attempts)

    @staticmethod
    def get_recommended_difficulty(db: Session, user_id: int) -> str:
        """Recommend difficulty based on recent performance"""
        accuracy = ReadingService.get_user_accuracy(db, user_id, limit=10)

        # Adaptive logic: aim for 70-80% success rate
        if accuracy >= 0.80:
            return "hard"
        elif accuracy >= 0.60:
            return "medium"
        else:
            return "easy"

    @staticmethod
    def get_next_reading_item(
        db: Session, user_id: int, difficulty: Optional[str] = None
    ) -> Optional[ReadingItem]:
        """Get next reading item for user with adaptive difficulty"""
        if not difficulty:
            difficulty = ReadingService.get_recommended_difficulty(db, user_id)

        # Get items the user hasn't completed yet
        completed_item_ids = (
            db.query(UserReadingAttempt.question_id)
            .join(ReadingQuestion)
            .filter(UserReadingAttempt.user_id == user_id)
            .distinct()
            .subquery()
        )

        # Find an item of appropriate difficulty that hasn't been completed
        reading_item = (
            db.query(ReadingItem)
            .filter(
                ReadingItem.difficulty == difficulty,
                ~ReadingItem.questions.any(
                    ReadingQuestion.id.in_(db.query(completed_item_ids))
                )
            )
            .first()
        )

        # If no new items at this difficulty, try any difficulty
        if not reading_item:
            reading_item = (
                db.query(ReadingItem)
                .filter(
                    ~ReadingItem.questions.any(
                        ReadingQuestion.id.in_(db.query(completed_item_ids))
                    )
                )
                .first()
            )

        # If all items completed, return any item
        if not reading_item:
            reading_item = db.query(ReadingItem).first()

        return reading_item

    @staticmethod
    def submit_answer(
        db: Session,
        user_id: int,
        question_id: int,
        user_answer: str,
        time_spent_seconds: Optional[int] = None
    ) -> Tuple[bool, ReadingQuestion, List[UserBadge]]:
        """Submit an answer and return feedback with any newly earned badges"""
        question = db.query(ReadingQuestion).filter(ReadingQuestion.id == question_id).first()
        if not question:
            return None

        is_correct = user_answer.upper() == question.correct_answer.upper()

        # Record attempt
        attempt = UserReadingAttempt(
            user_id=user_id,
            question_id=question_id,
            user_answer=user_answer.upper(),
            is_correct=is_correct,
            time_spent_seconds=time_spent_seconds
        )
        db.add(attempt)

        # Update user stats
        if is_correct:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.reading_items_completed = (user.reading_items_completed or 0) + 1

        db.commit()

        # Update quest progress
        QuestService.update_quest_progress(
            db,
            user_id,
            "reading_complete",
            {"skill_category": question.skill_category}
        )

        # Check and award badges
        newly_earned_badges = BadgeService.check_and_award_badges(db, user_id)

        return is_correct, question, newly_earned_badges

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict:
        """Get detailed reading statistics for user"""
        # Total attempts
        total_attempts = (
            db.query(func.count(UserReadingAttempt.id))
            .filter(UserReadingAttempt.user_id == user_id)
            .scalar()
        )

        # Correct answers
        correct_answers = (
            db.query(func.count(UserReadingAttempt.id))
            .filter(
                UserReadingAttempt.user_id == user_id,
                UserReadingAttempt.is_correct == True
            )
            .scalar()
        )

        # Overall accuracy
        accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0

        # Skill breakdown
        skill_breakdown = {}
        skills = (
            db.query(
                ReadingQuestion.skill_category,
                func.count(UserReadingAttempt.id).label("total"),
                func.sum(func.cast(UserReadingAttempt.is_correct, Integer)).label("correct")
            )
            .join(UserReadingAttempt)
            .filter(UserReadingAttempt.user_id == user_id)
            .group_by(ReadingQuestion.skill_category)
            .all()
        )

        for skill, total, correct in skills:
            if skill:
                skill_breakdown[skill] = {
                    "correct": correct or 0,
                    "total": total,
                    "accuracy": (correct / total * 100) if total > 0 else 0
                }

        # Get recent difficulty and recommendation
        recent_attempts = (
            db.query(ReadingItem.difficulty)
            .join(ReadingQuestion)
            .join(UserReadingAttempt)
            .filter(UserReadingAttempt.user_id == user_id)
            .order_by(UserReadingAttempt.attempted_at.desc())
            .limit(1)
            .first()
        )

        recent_difficulty = recent_attempts[0] if recent_attempts else "medium"
        recommended_difficulty = ReadingService.get_recommended_difficulty(db, user_id)

        return {
            "total_attempts": total_attempts,
            "correct_answers": correct_answers,
            "accuracy": round(accuracy, 2),
            "skill_breakdown": skill_breakdown,
            "recent_difficulty": recent_difficulty,
            "recommended_difficulty": recommended_difficulty
        }

    @staticmethod
    def get_available_items(db: Session) -> List[ReadingItem]:
        """Get all available reading items"""
        return db.query(ReadingItem).all()
