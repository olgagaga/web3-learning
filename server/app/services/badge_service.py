from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime
from app.models.quest import Badge, UserBadge, UserQuest
from app.models.user import User
from app.models.reading import UserReadingAttempt
from app.models.writing import Essay


class BadgeService:
    @staticmethod
    def get_all_badges(db: Session) -> List[Badge]:
        """Get all available badges"""
        return db.query(Badge).all()

    @staticmethod
    def get_user_badges(db: Session, user_id: int) -> List[UserBadge]:
        """Get all badges earned by a user"""
        return db.query(UserBadge).filter(UserBadge.user_id == user_id).all()

    @staticmethod
    def has_badge(db: Session, user_id: int, badge_id: int) -> bool:
        """Check if user already has a specific badge"""
        return (
            db.query(UserBadge)
            .filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
            .first()
            is not None
        )

    @staticmethod
    def award_badge(
        db: Session, user_id: int, badge_id: int, transaction_hash: Optional[str] = None
    ) -> Optional[UserBadge]:
        """Award a badge to a user"""
        # Check if user already has this badge
        if BadgeService.has_badge(db, user_id, badge_id):
            return None

        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            transaction_hash=transaction_hash,
        )

        db.add(user_badge)

        # Update user's badge count
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.badges_earned = (user.badges_earned or 0) + 1

        db.commit()
        db.refresh(user_badge)

        return user_badge

    @staticmethod
    def check_and_award_badges(db: Session, user_id: int) -> List[UserBadge]:
        """
        Check all badge criteria and award any earned badges
        Returns list of newly awarded badges
        """
        newly_awarded = []

        # Get all badges
        all_badges = BadgeService.get_all_badges(db)

        for badge in all_badges:
            # Skip if user already has this badge
            if BadgeService.has_badge(db, user_id, badge.id):
                continue

            # Check if user meets criteria
            if BadgeService._meets_badge_criteria(db, user_id, badge):
                user_badge = BadgeService.award_badge(db, user_id, badge.id)
                if user_badge:
                    newly_awarded.append(user_badge)

        return newly_awarded

    @staticmethod
    def _meets_badge_criteria(db: Session, user_id: int, badge: Badge) -> bool:
        """Check if user meets badge criteria"""
        criteria = badge.criteria

        # Reading accuracy criteria
        if "reading_accuracy" in criteria:
            required_accuracy = criteria["reading_accuracy"]
            items_required = criteria.get("items_completed", 50)

            total_attempts = (
                db.query(func.count(UserReadingAttempt.id))
                .filter(UserReadingAttempt.user_id == user_id)
                .scalar()
                or 0
            )

            if total_attempts < items_required:
                return False

            correct_answers = (
                db.query(func.count(UserReadingAttempt.id))
                .filter(
                    UserReadingAttempt.user_id == user_id,
                    UserReadingAttempt.is_correct == True,
                )
                .scalar()
                or 0
            )

            accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
            if accuracy < required_accuracy:
                return False

        # Writing average score criteria
        if "writing_avg_score" in criteria:
            required_avg = criteria["writing_avg_score"]
            essays_required = criteria.get("essays_written", 10)

            essay_count = (
                db.query(func.count(Essay.id))
                .filter(Essay.user_id == user_id)
                .scalar()
                or 0
            )

            if essay_count < essays_required:
                return False

            avg_score = (
                db.query(func.avg(Essay.overall_score))
                .filter(Essay.user_id == user_id)
                .scalar()
                or 0
            )

            if float(avg_score) < required_avg:
                return False

        # Minimum score criteria (for any single essay)
        if "min_score" in criteria:
            required_score = criteria["min_score"]

            max_score = (
                db.query(func.max(Essay.overall_score))
                .filter(Essay.user_id == user_id)
                .scalar()
                or 0
            )

            if float(max_score) < required_score:
                return False

        # Quests completed criteria
        if "quests_completed" in criteria:
            required_quests = criteria["quests_completed"]

            completed_quests = (
                db.query(func.count(UserQuest.id))
                .filter(UserQuest.user_id == user_id, UserQuest.status == "completed")
                .scalar()
                or 0
            )

            if completed_quests < required_quests:
                return False

        # Weekly quests criteria
        if "weekly_quests" in criteria:
            required_weekly = criteria["weekly_quests"]

            completed_weekly = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="weekly"),
                )
                .scalar()
                or 0
            )

            if completed_weekly < required_weekly:
                return False

        # Boss challenge criteria
        if "boss_reading" in criteria:
            required_boss = criteria["boss_reading"]

            completed_boss = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="boss", skill_focus="reading"),
                )
                .scalar()
                or 0
            )

            if completed_boss < required_boss:
                return False

        if "boss_writing" in criteria:
            required_boss = criteria["boss_writing"]

            completed_boss = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="boss", skill_focus="writing"),
                )
                .scalar()
                or 0
            )

            if completed_boss < required_boss:
                return False

        # If all criteria are met
        return True

    @staticmethod
    def get_badge_progress(db: Session, user_id: int, badge_id: int) -> Dict:
        """Get user's progress toward earning a specific badge"""
        badge = db.query(Badge).filter(Badge.id == badge_id).first()
        if not badge:
            return None

        # Check if already earned
        if BadgeService.has_badge(db, user_id, badge_id):
            return {
                "badge_id": badge_id,
                "earned": True,
                "progress": 100,
                "criteria_progress": {},
            }

        criteria = badge.criteria
        criteria_progress = {}

        # Calculate progress for each criteria
        if "reading_accuracy" in criteria:
            required_accuracy = criteria["reading_accuracy"]
            items_required = criteria.get("items_completed", 50)

            total_attempts = (
                db.query(func.count(UserReadingAttempt.id))
                .filter(UserReadingAttempt.user_id == user_id)
                .scalar()
                or 0
            )

            correct_answers = (
                db.query(func.count(UserReadingAttempt.id))
                .filter(
                    UserReadingAttempt.user_id == user_id,
                    UserReadingAttempt.is_correct == True,
                )
                .scalar()
                or 0
            )

            accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0

            criteria_progress["reading_accuracy"] = {
                "current": round(accuracy, 2),
                "required": required_accuracy,
                "items_completed": total_attempts,
                "items_required": items_required,
            }

        if "writing_avg_score" in criteria:
            required_avg = criteria["writing_avg_score"]
            essays_required = criteria.get("essays_written", 10)

            essay_count = (
                db.query(func.count(Essay.id))
                .filter(Essay.user_id == user_id)
                .scalar()
                or 0
            )

            avg_score = (
                db.query(func.avg(Essay.overall_score))
                .filter(Essay.user_id == user_id)
                .scalar()
                or 0
            )

            criteria_progress["writing_avg_score"] = {
                "current": round(float(avg_score), 2),
                "required": required_avg,
                "essays_written": essay_count,
                "essays_required": essays_required,
            }

        if "min_score" in criteria:
            required_score = criteria["min_score"]

            max_score = (
                db.query(func.max(Essay.overall_score))
                .filter(Essay.user_id == user_id)
                .scalar()
                or 0
            )

            criteria_progress["min_score"] = {
                "current": round(float(max_score), 2),
                "required": required_score,
            }

        if "quests_completed" in criteria:
            required_quests = criteria["quests_completed"]

            completed_quests = (
                db.query(func.count(UserQuest.id))
                .filter(UserQuest.user_id == user_id, UserQuest.status == "completed")
                .scalar()
                or 0
            )

            criteria_progress["quests_completed"] = {
                "current": completed_quests,
                "required": required_quests,
            }

        if "weekly_quests" in criteria:
            required_weekly = criteria["weekly_quests"]

            completed_weekly = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="weekly"),
                )
                .scalar()
                or 0
            )

            criteria_progress["weekly_quests"] = {
                "current": completed_weekly,
                "required": required_weekly,
            }

        if "boss_reading" in criteria:
            required_boss = criteria["boss_reading"]

            completed_boss = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="boss", skill_focus="reading"),
                )
                .scalar()
                or 0
            )

            criteria_progress["boss_reading"] = {
                "current": completed_boss,
                "required": required_boss,
            }

        if "boss_writing" in criteria:
            required_boss = criteria["boss_writing"]

            completed_boss = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="boss", skill_focus="writing"),
                )
                .scalar()
                or 0
            )

            criteria_progress["boss_writing"] = {
                "current": completed_boss,
                "required": required_boss,
            }

        # Calculate overall progress percentage
        total_criteria = len(criteria)
        met_criteria = sum(
            1
            for key in criteria
            if BadgeService._check_single_criterion(db, user_id, badge, key)
        )
        progress_percentage = (met_criteria / total_criteria * 100) if total_criteria > 0 else 0

        return {
            "badge_id": badge_id,
            "earned": False,
            "progress": round(progress_percentage, 2),
            "criteria_progress": criteria_progress,
        }

    @staticmethod
    def _check_single_criterion(
        db: Session, user_id: int, badge: Badge, criterion_key: str
    ) -> bool:
        """Check if a single criterion is met"""
        criteria = badge.criteria

        if criterion_key == "reading_accuracy":
            required_accuracy = criteria["reading_accuracy"]
            items_required = criteria.get("items_completed", 50)

            total_attempts = (
                db.query(func.count(UserReadingAttempt.id))
                .filter(UserReadingAttempt.user_id == user_id)
                .scalar() or 0
            )

            if total_attempts < items_required:
                return False

            correct_answers = (
                db.query(func.count(UserReadingAttempt.id))
                .filter(UserReadingAttempt.user_id == user_id, UserReadingAttempt.is_correct == True)
                .scalar() or 0
            )

            accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
            return accuracy >= required_accuracy

        if criterion_key == "writing_avg_score":
            required_avg = criteria["writing_avg_score"]
            essays_required = criteria.get("essays_written", 10)

            essay_count = (
                db.query(func.count(Essay.id))
                .filter(Essay.user_id == user_id)
                .scalar() or 0
            )

            if essay_count < essays_required:
                return False

            avg_score = (
                db.query(func.avg(Essay.overall_score))
                .filter(Essay.user_id == user_id)
                .scalar() or 0
            )

            return float(avg_score) >= required_avg

        if criterion_key == "min_score":
            required_score = criteria["min_score"]
            max_score = (
                db.query(func.max(Essay.overall_score))
                .filter(Essay.user_id == user_id)
                .scalar() or 0
            )
            return float(max_score) >= required_score

        if criterion_key == "quests_completed":
            required = criteria[criterion_key]
            completed = (
                db.query(func.count(UserQuest.id))
                .filter(UserQuest.user_id == user_id, UserQuest.status == "completed")
                .scalar() or 0
            )
            return completed >= required

        if criterion_key == "weekly_quests":
            required = criteria[criterion_key]
            completed = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="weekly"),
                )
                .scalar() or 0
            )
            return completed >= required

        if criterion_key == "boss_reading":
            required = criteria[criterion_key]
            completed = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="boss", skill_focus="reading"),
                )
                .scalar() or 0
            )
            return completed >= required

        if criterion_key == "boss_writing":
            required = criteria[criterion_key]
            completed = (
                db.query(func.count(UserQuest.id))
                .join(UserQuest.quest)
                .filter(
                    UserQuest.user_id == user_id,
                    UserQuest.status == "completed",
                    UserQuest.quest.has(quest_type="boss", skill_focus="writing"),
                )
                .scalar() or 0
            )
            return completed >= required

        # Special handling for non-specific criteria keys
        if criterion_key in ["items_completed", "essays_written"]:
            # These are sub-requirements, not standalone criteria
            return False

        return False

    @staticmethod
    def get_user_badge_showcase(db: Session, user_id: int) -> Dict:
        """Get a showcase of user's badges with statistics"""
        user_badges = BadgeService.get_user_badges(db, user_id)

        badge_categories = {
            "mastery": [],
            "achievement": [],
            "special": [],
        }

        for user_badge in user_badges:
            badge = user_badge.badge
            badge_categories[badge.badge_type].append(
                {
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "skill_level": badge.skill_level,
                    "icon_url": badge.icon_url,
                    "earned_at": user_badge.minted_at.isoformat(),
                    "on_chain": bool(user_badge.transaction_hash),
                }
            )

        return {
            "total_badges": len(user_badges),
            "mastery_badges": len(badge_categories["mastery"]),
            "achievement_badges": len(badge_categories["achievement"]),
            "special_badges": len(badge_categories["special"]),
            "badges_by_category": badge_categories,
        }
