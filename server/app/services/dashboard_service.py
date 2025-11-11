from sqlalchemy.orm import Session
from sqlalchemy import func, and_, Integer
from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.models.user import User
from app.models.reading import UserReadingAttempt, ReadingQuestion
from app.models.writing import Essay
from app.models.quest import UserQuest
from app.services.reading_service import ReadingService
from app.services.writing_service import WritingService
from app.services.quest_service import QuestService


class DashboardService:
    @staticmethod
    def get_comprehensive_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """Get all dashboard statistics for a user"""

        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Get individual module stats
        reading_stats = ReadingService.get_user_stats(db, user_id)
        writing_stats = WritingService.get_user_stats(db, user_id)
        quest_stats = QuestService.get_quest_stats(db, user_id)

        # Get activity timeline (last 30 days)
        activity_timeline = DashboardService._get_activity_timeline(db, user_id, days=30)

        # Get recent achievements
        recent_achievements = DashboardService._get_recent_achievements(db, user_id)

        # Calculate overall progress
        overall_progress = DashboardService._calculate_overall_progress(
            reading_stats, writing_stats, quest_stats
        )

        # Get streak information
        streak_info = DashboardService._get_streak_info(db, user_id)

        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "current_streak": user.current_streak,
                "reading_items_completed": user.reading_items_completed,
                "essays_written": user.essays_written,
                "badges_earned": user.badges_earned,
            },
            "reading_stats": reading_stats,
            "writing_stats": writing_stats,
            "quest_stats": quest_stats,
            "activity_timeline": activity_timeline,
            "recent_achievements": recent_achievements,
            "overall_progress": overall_progress,
            "streak_info": streak_info,
        }

    @staticmethod
    def _get_activity_timeline(db: Session, user_id: int, days: int = 30) -> List[Dict]:
        """Get daily activity for the last N days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get reading activity by day
        reading_by_day = {}
        reading_attempts = (
            db.query(
                func.date(UserReadingAttempt.attempted_at).label("date"),
                func.count(UserReadingAttempt.id).label("count")
            )
            .filter(
                UserReadingAttempt.user_id == user_id,
                UserReadingAttempt.attempted_at >= start_date
            )
            .group_by(func.date(UserReadingAttempt.attempted_at))
            .all()
        )
        for date, count in reading_attempts:
            reading_by_day[str(date)] = count

        # Get writing activity by day
        writing_by_day = {}
        essays_by_day = (
            db.query(
                func.date(Essay.created_at).label("date"),
                func.count(Essay.id).label("count")
            )
            .filter(
                Essay.user_id == user_id,
                Essay.created_at >= start_date
            )
            .group_by(func.date(Essay.created_at))
            .all()
        )
        for date, count in essays_by_day:
            writing_by_day[str(date)] = count

        # Build timeline
        timeline = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            reading_count = reading_by_day.get(date_str, 0)
            writing_count = writing_by_day.get(date_str, 0)

            timeline.append({
                "date": date_str,
                "reading_items": reading_count,
                "essays": writing_count,
                "total_activity": reading_count + writing_count
            })

        return timeline

    @staticmethod
    def _get_recent_achievements(db: Session, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent quest completions and badges"""
        achievements = []

        # Recent completed quests
        completed_quests = (
            db.query(UserQuest)
            .filter(
                UserQuest.user_id == user_id,
                UserQuest.status == "completed"
            )
            .order_by(UserQuest.completed_at.desc())
            .limit(limit)
            .all()
        )

        for uq in completed_quests:
            if uq.quest and uq.completed_at:
                achievements.append({
                    "type": "quest_completed",
                    "title": uq.quest.title,
                    "description": f"Completed {uq.quest.quest_type} quest",
                    "points": uq.quest.reward_points,
                    "date": uq.completed_at.isoformat(),
                })

        # Sort by date
        achievements.sort(key=lambda x: x["date"], reverse=True)
        return achievements[:limit]

    @staticmethod
    def _calculate_overall_progress(
        reading_stats: Dict, writing_stats: Dict, quest_stats: Dict
    ) -> Dict:
        """Calculate overall learning progress"""

        # Reading progress (based on items completed and accuracy)
        reading_items = reading_stats["total_attempts"]
        reading_accuracy = reading_stats["accuracy"]
        reading_score = min(100, (reading_items / 100) * 50 + (reading_accuracy / 100) * 50)

        # Writing progress (based on essays and average score)
        essays_count = writing_stats["total_essays"]
        writing_avg = writing_stats["average_score"]
        writing_score = min(100, (essays_count / 20) * 50 + (writing_avg / 9) * 50)

        # Quest progress (based on completion rate)
        quest_completion = quest_stats["completed_quests"]
        quest_score = min(100, (quest_completion / 10) * 100)

        # Overall progress (weighted average)
        overall = (reading_score * 0.35 + writing_score * 0.35 + quest_score * 0.30)

        return {
            "overall_percentage": round(overall, 1),
            "reading_percentage": round(reading_score, 1),
            "writing_percentage": round(writing_score, 1),
            "quest_percentage": round(quest_score, 1),
            "level": DashboardService._calculate_level(overall),
        }

    @staticmethod
    def _calculate_level(progress_percentage: float) -> Dict:
        """Calculate user level based on progress"""
        level = int(progress_percentage / 10) + 1
        level = max(1, min(10, level))  # Level 1-10

        return {
            "current_level": level,
            "max_level": 10,
            "progress_to_next": round((progress_percentage % 10) * 10, 1)
        }

    @staticmethod
    def _get_streak_info(db: Session, user_id: int) -> Dict:
        """Get detailed streak information"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"current_streak": 0, "longest_streak": 0}

        # Get activity for last 60 days to calculate longest streak
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=60)

        # Get all active dates
        reading_dates = set()
        reading_attempts = (
            db.query(func.date(UserReadingAttempt.attempted_at))
            .filter(
                UserReadingAttempt.user_id == user_id,
                UserReadingAttempt.attempted_at >= start_date
            )
            .distinct()
            .all()
        )
        reading_dates = {str(date[0]) for date in reading_attempts}

        writing_dates = set()
        essay_dates = (
            db.query(func.date(Essay.created_at))
            .filter(
                Essay.user_id == user_id,
                Essay.created_at >= start_date
            )
            .distinct()
            .all()
        )
        writing_dates = {str(date[0]) for date in essay_dates}

        active_dates = reading_dates.union(writing_dates)

        # Calculate longest streak
        longest_streak = 0
        current_streak_calc = 0

        for i in range(60):
            date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in active_dates:
                current_streak_calc += 1
                longest_streak = max(longest_streak, current_streak_calc)
            else:
                if i == 0:  # Today
                    continue  # Don't break streak if today has no activity yet
                current_streak_calc = 0

        return {
            "current_streak": user.current_streak or 0,
            "longest_streak": longest_streak,
            "total_active_days": len(active_dates),
        }

    @staticmethod
    def get_weekly_summary(db: Session, user_id: int) -> Dict:
        """Get weekly summary statistics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        # Reading activity
        reading_count = (
            db.query(func.count(UserReadingAttempt.id))
            .filter(
                UserReadingAttempt.user_id == user_id,
                UserReadingAttempt.attempted_at >= start_date
            )
            .scalar() or 0
        )

        reading_correct = (
            db.query(func.count(UserReadingAttempt.id))
            .filter(
                UserReadingAttempt.user_id == user_id,
                UserReadingAttempt.attempted_at >= start_date,
                UserReadingAttempt.is_correct == True
            )
            .scalar() or 0
        )

        # Writing activity
        essays_count = (
            db.query(func.count(Essay.id))
            .filter(
                Essay.user_id == user_id,
                Essay.created_at >= start_date
            )
            .scalar() or 0
        )

        avg_score = (
            db.query(func.avg(Essay.overall_score))
            .filter(
                Essay.user_id == user_id,
                Essay.created_at >= start_date
            )
            .scalar() or 0
        )

        # Quests completed
        quests_completed = (
            db.query(func.count(UserQuest.id))
            .filter(
                UserQuest.user_id == user_id,
                UserQuest.status == "completed",
                UserQuest.completed_at >= start_date
            )
            .scalar() or 0
        )

        return {
            "period": "last_7_days",
            "reading_items": reading_count,
            "reading_accuracy": round((reading_correct / reading_count * 100) if reading_count > 0 else 0, 1),
            "essays_written": essays_count,
            "average_essay_score": round(float(avg_score), 1) if avg_score else 0,
            "quests_completed": quests_completed,
            "total_activities": reading_count + essays_count,
        }
