"""
Attestation service for monitoring user progress and generating signed attestations
Checks daily activity and automatically creates attestations for active commitments
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.staking import Commitment, CommitmentStatus, CommitmentType
from app.models.user import User
from app.models.reading import UserReadingAttempt
from app.models.writing import Essay
from app.services.web3_service import get_web3_service
from app.services.staking_service import StakingService


class AttestationService:
    """Service for monitoring progress and generating attestations"""

    @staticmethod
    def calculate_streak_progress(db: Session, user_id: int, start_date: datetime) -> int:
        """
        Calculate current streak progress since commitment start date
        Returns number of consecutive days with activity
        """
        current_date = start_date.date()
        today = datetime.utcnow().date()
        streak = 0

        while current_date <= today:
            has_activity = AttestationService.has_daily_activity(
                db, user_id, current_date
            )

            if has_activity:
                streak += 1
                current_date += timedelta(days=1)
            else:
                # Check if it's today (grace period)
                if current_date == today:
                    # Don't break streak on current day
                    break
                else:
                    # Streak broken
                    break

        return streak

    @staticmethod
    def has_daily_activity(db: Session, user_id: int, date: datetime.date) -> bool:
        """
        Check if user has any activity on a specific date
        Activity can be reading or writing
        """
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())

        # Check reading attempts
        reading_count = db.query(UserReadingAttempt).filter(
            and_(
                UserReadingAttempt.user_id == user_id,
                UserReadingAttempt.attempted_at >= start_of_day,
                UserReadingAttempt.attempted_at <= end_of_day
            )
        ).count()

        if reading_count > 0:
            return True

        # Check essays
        essay_count = db.query(Essay).filter(
            and_(
                Essay.user_id == user_id,
                Essay.created_at >= start_of_day,
                Essay.created_at <= end_of_day
            )
        ).count()

        return essay_count > 0

    @staticmethod
    def calculate_reading_progress(db: Session, user_id: int, start_date: datetime, target: int) -> int:
        """Calculate reading items completed since start date"""
        count = db.query(UserReadingAttempt).filter(
            and_(
                UserReadingAttempt.user_id == user_id,
                UserReadingAttempt.attempted_at >= start_date
            )
        ).count()

        return min(count, target)

    @staticmethod
    def calculate_writing_progress(db: Session, user_id: int, start_date: datetime, target: int) -> int:
        """Calculate essays written since start date"""
        count = db.query(Essay).filter(
            and_(
                Essay.user_id == user_id,
                Essay.created_at >= start_date
            )
        ).count()

        return min(count, target)

    @staticmethod
    def calculate_commitment_progress(
        db: Session,
        commitment: Commitment
    ) -> int:
        """
        Calculate current progress for a commitment based on type
        Returns current progress value
        """
        if commitment.commitment_type in [CommitmentType.STREAK_7_DAY, CommitmentType.STREAK_30_DAY]:
            return AttestationService.calculate_streak_progress(
                db, commitment.user_id, commitment.start_date
            )
        elif commitment.commitment_type == CommitmentType.READING_GOAL:
            return AttestationService.calculate_reading_progress(
                db, commitment.user_id, commitment.start_date, commitment.target_value
            )
        elif commitment.commitment_type == CommitmentType.WRITING_GOAL:
            return AttestationService.calculate_writing_progress(
                db, commitment.user_id, commitment.start_date, commitment.target_value
            )
        else:
            return commitment.current_progress

    @staticmethod
    def check_commitment_progress(
        db: Session,
        commitment_id: int
    ) -> Dict[str, Any]:
        """
        Check progress for a specific commitment
        Returns progress info and whether attestation is needed
        """
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()

        if not commitment:
            raise ValueError("Commitment not found")

        if commitment.status != CommitmentStatus.ACTIVE:
            return {
                "commitment_id": commitment_id,
                "status": commitment.status,
                "current_progress": commitment.current_progress,
                "needs_attestation": False
            }

        # Calculate actual progress
        actual_progress = AttestationService.calculate_commitment_progress(db, commitment)

        # Check if progress has increased
        needs_attestation = actual_progress > commitment.current_progress

        return {
            "commitment_id": commitment_id,
            "status": commitment.status,
            "stored_progress": commitment.current_progress,
            "actual_progress": actual_progress,
            "target_value": commitment.target_value,
            "needs_attestation": needs_attestation,
            "is_completed": actual_progress >= commitment.target_value
        }

    @staticmethod
    def generate_attestation_for_commitment(
        db: Session,
        commitment_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a signed attestation for a commitment if progress has increased
        Returns attestation data or None if no update needed
        """
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()

        if not commitment:
            raise ValueError("Commitment not found")

        if commitment.status != CommitmentStatus.ACTIVE:
            return None

        # Get user wallet
        from app.models.staking import Wallet
        wallet = db.query(Wallet).filter(Wallet.user_id == commitment.user_id).first()

        if not wallet:
            raise ValueError("User wallet not found")

        # Calculate progress
        progress_info = AttestationService.check_commitment_progress(db, commitment_id)

        if not progress_info["needs_attestation"]:
            return None

        actual_progress = progress_info["actual_progress"]

        # Generate attestation
        web3_service = get_web3_service()

        attestation_hash = web3_service.generate_attestation_hash(
            commitment_id=commitment.id,
            user_address=wallet.wallet_address,
            progress=actual_progress
        )

        signature_data = web3_service.sign_attestation(
            commitment_id=commitment.id,
            user_address=wallet.wallet_address,
            progress=actual_progress,
            attestation_hash=attestation_hash
        )

        # Collect activity IDs as proof
        activity_ids = AttestationService.get_activity_proof(
            db, commitment.user_id, commitment.start_date, commitment.commitment_type
        )

        # Store attestation in database
        attestation = StakingService.create_attestation(
            db=db,
            commitment_id=commitment.id,
            user_id=commitment.user_id,
            progress_value=actual_progress,
            activity_type=commitment.commitment_type,
            activity_ids=activity_ids,
            signature=signature_data["signature"],
            signature_hash=signature_data["message_hash"],
            attestation_hash=attestation_hash
        )

        return {
            "commitment_id": commitment.id,
            "progress": actual_progress,
            "target_value": commitment.target_value,
            "attestation_hash": attestation_hash,
            "signature": signature_data["signature"],
            "message_hash": signature_data["message_hash"],
            "signer": signature_data["signer"],
            "attestation_id": attestation.id,
            "is_completed": actual_progress >= commitment.target_value
        }

    @staticmethod
    def get_activity_proof(
        db: Session,
        user_id: int,
        since_date: datetime,
        commitment_type: CommitmentType
    ) -> List[int]:
        """
        Get activity IDs as proof for attestation
        Returns list of reading attempt IDs or essay IDs
        """
        if commitment_type == CommitmentType.READING_GOAL:
            attempts = db.query(UserReadingAttempt.id).filter(
                and_(
                    UserReadingAttempt.user_id == user_id,
                    UserReadingAttempt.attempted_at >= since_date
                )
            ).limit(100).all()
            return [attempt.id for attempt in attempts]

        elif commitment_type == CommitmentType.WRITING_GOAL:
            essays = db.query(Essay.id).filter(
                and_(
                    Essay.user_id == user_id,
                    Essay.created_at >= since_date
                )
            ).limit(100).all()
            return [essay.id for essay in essays]

        else:
            # For streak-based commitments, get recent activity
            reading_ids = db.query(UserReadingAttempt.id).filter(
                and_(
                    UserReadingAttempt.user_id == user_id,
                    UserReadingAttempt.attempted_at >= since_date
                )
            ).limit(50).all()

            essay_ids = db.query(Essay.id).filter(
                and_(
                    Essay.user_id == user_id,
                    Essay.created_at >= since_date
                )
            ).limit(50).all()

            return [r.id for r in reading_ids] + [e.id for e in essay_ids]

    @staticmethod
    def check_all_active_commitments(db: Session) -> List[Dict[str, Any]]:
        """
        Check all active commitments and generate attestations where needed
        This should be run periodically (e.g., daily cron job)
        Returns list of generated attestations
        """
        active_commitments = db.query(Commitment).filter(
            Commitment.status == CommitmentStatus.ACTIVE
        ).all()

        results = []

        for commitment in active_commitments:
            try:
                attestation = AttestationService.generate_attestation_for_commitment(
                    db, commitment.id
                )

                if attestation:
                    results.append({
                        "commitment_id": commitment.id,
                        "user_id": commitment.user_id,
                        "progress": attestation["progress"],
                        "success": True,
                        "attestation": attestation
                    })
                else:
                    results.append({
                        "commitment_id": commitment.id,
                        "user_id": commitment.user_id,
                        "success": True,
                        "message": "No progress update needed"
                    })

            except Exception as e:
                results.append({
                    "commitment_id": commitment.id,
                    "user_id": commitment.user_id,
                    "success": False,
                    "error": str(e)
                })

        return results

    @staticmethod
    def get_commitment_summary(
        db: Session,
        commitment_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive summary of commitment progress
        Includes milestone history and current status
        """
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()

        if not commitment:
            raise ValueError("Commitment not found")

        # Get attestations
        attestations = StakingService.get_commitment_attestations(db, commitment_id)

        # Calculate current progress
        current_progress = AttestationService.calculate_commitment_progress(db, commitment)

        # Get daily activity breakdown for streaks
        daily_activity = []
        if commitment.commitment_type in [CommitmentType.STREAK_7_DAY, CommitmentType.STREAK_30_DAY]:
            start_date = commitment.start_date.date()
            today = datetime.utcnow().date()
            current_date = start_date

            while current_date <= today:
                has_activity = AttestationService.has_daily_activity(
                    db, commitment.user_id, current_date
                )
                daily_activity.append({
                    "date": current_date.isoformat(),
                    "has_activity": has_activity
                })
                current_date += timedelta(days=1)

        return {
            "commitment": {
                "id": commitment.id,
                "type": commitment.commitment_type,
                "status": commitment.status,
                "target_value": commitment.target_value,
                "current_progress": current_progress,
                "stored_progress": commitment.current_progress,
                "start_date": commitment.start_date.isoformat(),
                "end_date": commitment.end_date.isoformat(),
                "stake_amount": str(commitment.stake_amount),
                "reward_amount": str(commitment.reward_amount) if commitment.reward_amount else None
            },
            "attestations": [
                {
                    "id": att.id,
                    "progress_value": att.progress_value,
                    "milestone_date": att.milestone_date.isoformat(),
                    "is_valid": att.is_valid
                } for att in attestations
            ],
            "daily_activity": daily_activity if daily_activity else None,
            "progress_percentage": (current_progress / commitment.target_value * 100) if commitment.target_value > 0 else 0,
            "days_remaining": (commitment.end_date - datetime.utcnow()).days if commitment.end_date > datetime.utcnow() else 0
        }


# Singleton accessor
def get_attestation_service() -> AttestationService:
    """Get attestation service"""
    return AttestationService()
