from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.services.auth import get_current_active_user
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard statistics"""
    stats = DashboardService.get_comprehensive_stats(db, current_user.id)
    return stats


@router.get("/weekly")
async def get_weekly_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get weekly summary statistics"""
    summary = DashboardService.get_weekly_summary(db, current_user.id)
    return summary
