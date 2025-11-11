from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.api.schemas.user import (
    UserResponse,
    UserProfileUpdate,
    PasswordChange,
    UserPreferences,
    UserPreferencesResponse,
)
from app.services.auth import (
    get_current_active_user,
    get_password_hash,
    verify_password,
    get_user_by_email,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""

    # Check if email is being changed and if it's already taken
    if profile_data.email and profile_data.email != current_user.email:
        existing_user = get_user_by_email(db, profile_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = profile_data.email

    # Update name if provided
    if profile_data.name:
        current_user.name = profile_data.name

    db.commit()
    db.refresh(current_user)

    return UserResponse.from_orm(current_user)


@router.post("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""

    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password (you can add more validation)
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    # For now, return default preferences
    # In a real app, you'd store these in a user_preferences table
    return UserPreferencesResponse(
        daily_reading_goal=5,
        daily_writing_goal=1,
        email_notifications=True,
        push_notifications=True,
        difficulty_preference="medium"
    )


@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    # For now, just return the preferences
    # In a real app, you'd save these to a user_preferences table
    return UserPreferencesResponse(**preferences.dict())


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""

    # Delete user (cascade will handle related records)
    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully"}


@router.get("/export")
async def export_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export user data"""
    from app.models.reading import UserReadingAttempt
    from app.models.writing import Essay
    from app.models.quest import UserQuest, UserBadge

    # Get all user data
    reading_attempts = db.query(UserReadingAttempt).filter(
        UserReadingAttempt.user_id == current_user.id
    ).count()

    essays = db.query(Essay).filter(
        Essay.user_id == current_user.id
    ).count()

    quests = db.query(UserQuest).filter(
        UserQuest.user_id == current_user.id
    ).count()

    badges = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).count()

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat(),
            "current_streak": current_user.current_streak,
        },
        "statistics": {
            "reading_attempts": reading_attempts,
            "essays_written": essays,
            "quests_taken": quests,
            "badges_earned": badges,
        }
    }
