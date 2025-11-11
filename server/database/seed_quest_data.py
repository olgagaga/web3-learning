"""
Seed script for quest data
Run with: python -m database.seed_quest_data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal
from app.models.quest import Quest, Badge


def seed_quest_data():
    db = SessionLocal()

    try:
        # Check if data already exists
        existing = db.query(Quest).first()
        if existing:
            print("Quest data already exists. Skipping seed.")
            return

        print("Seeding quest data...")

        # BEGINNER QUESTS
        quest1 = Quest(
            title="First Steps",
            description="Start your learning journey by completing your first reading practice and essay",
            quest_type="skill",
            skill_focus="general",
            requirements={
                "reading_items": 5,
                "essays": 1
            },
            reward_points=100,
            reward_badge="beginner_badge",
            is_active=True
        )

        quest2 = Quest(
            title="Reading Explorer",
            description="Master reading comprehension by completing 10 reading items with good accuracy",
            quest_type="skill",
            skill_focus="reading",
            requirements={
                "reading_items": 10
            },
            reward_points=200,
            reward_badge=None,
            is_active=True
        )

        quest3 = Quest(
            title="Writing Warrior",
            description="Improve your writing skills by completing 3 essays",
            quest_type="skill",
            skill_focus="writing",
            requirements={
                "essays": 3
            },
            reward_points=300,
            reward_badge=None,
            is_active=True
        )

        quest4 = Quest(
            title="Inference Master",
            description="Complete 15 reading items focusing on inference skills",
            quest_type="skill",
            skill_focus="inference",
            requirements={
                "reading_items": 15
            },
            reward_points=250,
            reward_badge=None,
            is_active=True
        )

        quest5 = Quest(
            title="Writing Excellence",
            description="Write an essay scoring 7.0 or higher",
            quest_type="skill",
            skill_focus="writing",
            requirements={
                "essays": 1,
                "min_score": 7.0
            },
            reward_points=500,
            reward_badge="excellence_badge",
            is_active=True
        )

        # DAILY QUESTS
        quest6 = Quest(
            title="Daily Practice",
            description="Complete your daily practice: 3 reading items and maintain your streak",
            quest_type="daily",
            skill_focus="general",
            requirements={
                "reading_items": 3
            },
            reward_points=50,
            reward_badge=None,
            is_active=True
        )

        quest7 = Quest(
            title="Daily Writing",
            description="Write one essay today to keep improving",
            quest_type="daily",
            skill_focus="writing",
            requirements={
                "essays": 1
            },
            reward_points=75,
            reward_badge=None,
            is_active=True
        )

        # WEEKLY QUESTS
        quest8 = Quest(
            title="Weekly Champion",
            description="Complete 20 reading items and 2 essays this week",
            quest_type="weekly",
            skill_focus="general",
            requirements={
                "reading_items": 20,
                "essays": 2
            },
            reward_points=1000,
            reward_badge="weekly_champion",
            is_active=True
        )

        # BOSS CHALLENGES
        quest9 = Quest(
            title="Boss Challenge: Reading Sprint",
            description="Complete a timed reading challenge with 10 questions in 20 minutes",
            quest_type="boss",
            skill_focus="reading",
            requirements={
                "boss_challenges": 1,
                "reading_items": 10
            },
            reward_points=750,
            reward_badge="reading_boss",
            is_active=True
        )

        quest10 = Quest(
            title="Boss Challenge: Essay Master",
            description="Write a high-quality essay (7.5+) in 40 minutes",
            quest_type="boss",
            skill_focus="writing",
            requirements={
                "boss_challenges": 1,
                "essays": 1,
                "min_score": 7.5
            },
            reward_points=1000,
            reward_badge="writing_boss",
            is_active=True
        )

        # Add all quests
        quests = [quest1, quest2, quest3, quest4, quest5, quest6, quest7, quest8, quest9, quest10]
        for quest in quests:
            db.add(quest)

        # Create Badges
        badge1 = Badge(
            name="Beginner Badge",
            description="Completed your first quest!",
            badge_type="achievement",
            skill_level="L1",
            icon_url="/badges/beginner.png",
            criteria={"quests_completed": 1}
        )

        badge2 = Badge(
            name="Reading Mastery L1",
            description="Mastered basic reading comprehension",
            badge_type="mastery",
            skill_level="L1",
            icon_url="/badges/reading-l1.png",
            criteria={"reading_accuracy": 70, "items_completed": 50}
        )

        badge3 = Badge(
            name="Writing Mastery L1",
            description="Achieved consistent writing scores above 6.5",
            badge_type="mastery",
            skill_level="L1",
            icon_url="/badges/writing-l1.png",
            criteria={"writing_avg_score": 6.5, "essays_written": 10}
        )

        badge4 = Badge(
            name="Excellence Badge",
            description="Achieved exceptional performance (7.0+)",
            badge_type="achievement",
            skill_level="L2",
            icon_url="/badges/excellence.png",
            criteria={"min_score": 7.0}
        )

        badge5 = Badge(
            name="Weekly Champion",
            description="Completed weekly challenge",
            badge_type="achievement",
            skill_level="L2",
            icon_url="/badges/weekly.png",
            criteria={"weekly_quests": 1}
        )

        badge6 = Badge(
            name="Reading Boss Conqueror",
            description="Defeated the Reading Boss Challenge",
            badge_type="special",
            skill_level="L3",
            icon_url="/badges/boss-reading.png",
            criteria={"boss_reading": 1}
        )

        badge7 = Badge(
            name="Writing Boss Conqueror",
            description="Defeated the Writing Boss Challenge",
            badge_type="special",
            skill_level="L3",
            icon_url="/badges/boss-writing.png",
            criteria={"boss_writing": 1}
        )

        # Add all badges
        badges = [badge1, badge2, badge3, badge4, badge5, badge6, badge7]
        for badge in badges:
            db.add(badge)

        db.commit()
        print(f"✅ Successfully seeded {len(quests)} quests and {len(badges)} badges!")

    except Exception as e:
        print(f"❌ Error seeding quest data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_quest_data()
