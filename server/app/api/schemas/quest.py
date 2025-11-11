from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from datetime import datetime


class QuestBase(BaseModel):
    title: str
    description: Optional[str] = None
    quest_type: str  # daily, weekly, skill, boss
    skill_focus: Optional[str] = None
    requirements: Dict[str, Any]  # {"reading_items": 10, "essays": 1, "min_score": 70}
    reward_points: int = 0
    reward_badge: Optional[str] = None


class QuestResponse(QuestBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserQuestProgress(BaseModel):
    id: int
    quest_id: int
    quest: QuestResponse
    status: str  # active, completed, failed
    progress: Dict[str, Any]  # {"reading_items": 5, "essays": 0}
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestAcceptRequest(BaseModel):
    quest_id: int


class QuestProgressUpdate(BaseModel):
    progress: Dict[str, Any]


class BadgeBase(BaseModel):
    name: str
    description: Optional[str] = None
    badge_type: str  # mastery, achievement, special
    skill_level: Optional[str] = None
    icon_url: Optional[str] = None
    criteria: Dict[str, Any]


class BadgeResponse(BadgeBase):
    id: int
    blockchain_address: Optional[str] = None
    token_id: Optional[str] = None
    metadata_uri: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AllBadgesResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    badge_type: str
    skill_level: Optional[str] = None
    icon_url: Optional[str] = None
    criteria: Dict[str, Any]
    blockchain_address: Optional[str] = None
    token_id: Optional[str] = None
    metadata_uri: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    id: int
    badge_id: int
    badge: BadgeResponse
    transaction_hash: Optional[str] = None
    minted_at: datetime

    class Config:
        from_attributes = True


class QuestStats(BaseModel):
    total_quests: int
    active_quests: int
    completed_quests: int
    total_points_earned: int
    badges_earned: int
