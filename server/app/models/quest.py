from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    quest_type = Column(String(50), nullable=False)  # daily, weekly, skill, boss
    skill_focus = Column(String(100))  # inference, writing-coherence, etc.
    requirements = Column(JSON, nullable=False)  # {"reading_items": 10, "essays": 1, "min_score": 70}
    reward_points = Column(Integer, default=0)
    reward_badge = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user_quests = relationship("UserQuest", back_populates="quest", cascade="all, delete-orphan")


class UserQuest(Base):
    __tablename__ = "user_quests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quest_id = Column(Integer, ForeignKey("quests.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="active")  # active, completed, failed
    progress = Column(JSON, default={})  # {"reading_items": 5, "essays": 0}
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    quest = relationship("Quest", back_populates="user_quests")


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    badge_type = Column(String(50), nullable=False)  # mastery, achievement, special
    skill_level = Column(String(50))  # L1, L2, L3, etc.
    icon_url = Column(String(500))
    criteria = Column(JSON, nullable=False)  # {"reading_accuracy": 80, "items_completed": 50}

    # Web3 data
    blockchain_address = Column(String(255))
    token_id = Column(String(255))
    metadata_uri = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)

    # Web3 transaction data
    transaction_hash = Column(String(255))
    minted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    badge = relationship("Badge", back_populates="user_badges")
