from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.models.quest import Quest, UserQuest, Badge, UserBadge
from app.models.user import User


class QuestService:
    @staticmethod
    def get_active_quests(db: Session) -> List[Quest]:
        """Get all active quests"""
        return db.query(Quest).filter(Quest.is_active == True).all()

    @staticmethod
    def get_user_quests(db: Session, user_id: int) -> List[UserQuest]:
        """Get all quests for a user"""
        return db.query(UserQuest).filter(UserQuest.user_id == user_id).all()

    @staticmethod
    def get_user_active_quests(db: Session, user_id: int) -> List[UserQuest]:
        """Get active quests for a user"""
        return (
            db.query(UserQuest)
            .filter(UserQuest.user_id == user_id, UserQuest.status == "active")
            .all()
        )

    @staticmethod
    def accept_quest(db: Session, user_id: int, quest_id: int) -> UserQuest:
        """Accept a quest"""
        # Check if user already has this quest
        existing = (
            db.query(UserQuest)
            .filter(UserQuest.user_id == user_id, UserQuest.quest_id == quest_id)
            .first()
        )

        if existing:
            return existing

        # Get quest to initialize progress
        quest = db.query(Quest).filter(Quest.id == quest_id).first()
        if not quest:
            raise ValueError("Quest not found")

        # Initialize progress based on requirements
        initial_progress = {}
        for key in quest.requirements:
            if key != "min_score":
                initial_progress[key] = 0

        user_quest = UserQuest(
            user_id=user_id,
            quest_id=quest_id,
            status="active",
            progress=initial_progress,
        )

        db.add(user_quest)
        db.commit()
        db.refresh(user_quest)

        return user_quest

    @staticmethod
    def update_quest_progress(
        db: Session,
        user_id: int,
        activity_type: str,
        activity_data: Dict[str, Any] = None,
    ) -> List[UserQuest]:
        """
        Update quest progress based on user activity
        activity_type: 'reading_complete', 'essay_complete', 'boss_challenge_complete'
        activity_data: additional data like scores, skill categories, etc.
        """
        updated_quests = []

        # Get all active quests for the user
        active_quests = QuestService.get_user_active_quests(db, user_id)

        for user_quest in active_quests:
            quest = user_quest.quest
            progress = user_quest.progress or {}
            requirements = quest.requirements

            # Update progress based on activity type
            if activity_type == "reading_complete":
                if "reading_items" in requirements:
                    current = progress.get("reading_items", 0)
                    progress["reading_items"] = current + 1

            elif activity_type == "essay_complete":
                if "essays" in requirements:
                    current = progress.get("essays", 0)
                    progress["essays"] = current + 1

                # Check minimum score if required
                if "min_score" in requirements and activity_data:
                    min_score = requirements["min_score"]
                    actual_score = activity_data.get("overall_score", 0)
                    if actual_score >= min_score:
                        progress["min_score_achieved"] = True

            elif activity_type == "boss_challenge_complete":
                if "boss_challenges" in requirements:
                    current = progress.get("boss_challenges", 0)
                    progress["boss_challenges"] = current + 1

            # Update the progress
            user_quest.progress = progress
            # Mark the JSON field as modified so SQLAlchemy updates it
            flag_modified(user_quest, "progress")

            # Check if quest is completed
            if QuestService._is_quest_completed(requirements, progress):
                user_quest.status = "completed"
                user_quest.completed_at = datetime.utcnow()

                # Award points and badge
                user = db.query(User).filter(User.id == user_id).first()
                if user and quest.reward_points:
                    # You can add a points field to User model if needed
                    pass

                if quest.reward_badge:
                    # Award badge (implement badge awarding logic)
                    pass

            updated_quests.append(user_quest)

        db.commit()
        for uq in updated_quests:
            db.refresh(uq)

        return updated_quests

    @staticmethod
    def _is_quest_completed(requirements: Dict, progress: Dict) -> bool:
        """Check if quest requirements are met"""
        for key, required_value in requirements.items():
            if key == "min_score":
                # Check if min_score was achieved
                if not progress.get("min_score_achieved", False):
                    return False
            else:
                # Check if count requirements are met
                current_value = progress.get(key, 0)
                if current_value < required_value:
                    return False

        return True

    @staticmethod
    def get_quest_stats(db: Session, user_id: int) -> Dict[str, int]:
        """Get quest statistics for a user"""
        user_quests = db.query(UserQuest).filter(UserQuest.user_id == user_id).all()

        active = sum(1 for uq in user_quests if uq.status == "active")
        completed = sum(1 for uq in user_quests if uq.status == "completed")

        # Calculate total points earned
        total_points = 0
        for uq in user_quests:
            if uq.status == "completed" and uq.quest:
                total_points += uq.quest.reward_points or 0

        # Get badges count
        badges_count = (
            db.query(UserBadge).filter(UserBadge.user_id == user_id).count()
        )

        return {
            "total_quests": len(user_quests),
            "active_quests": active,
            "completed_quests": completed,
            "total_points_earned": total_points,
            "badges_earned": badges_count,
        }

    @staticmethod
    def get_user_badges(db: Session, user_id: int) -> List[UserBadge]:
        """Get all badges earned by a user"""
        return db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
