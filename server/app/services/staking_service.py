"""
Staking service for managing commitments and pods
Integrates database operations with blockchain interactions
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.staking import (
    Commitment, CommitmentStatus, CommitmentType,
    Pod, PodStatus,
    PodMembership,
    StakingTransaction, TransactionType,
    MilestoneAttestation,
    ScholarshipPool
)
from app.models.user import User
from app.services.web3_service import get_web3_service


class StakingService:
    """Service for staking and commitment management"""

    @staticmethod
    def create_commitment(
        db: Session,
        user_id: int,
        commitment_type: CommitmentType,
        target_value: int,
        duration_days: int,
        stake_amount: Decimal,
        pod_id: Optional[int] = None,
        contract_address: Optional[str] = None,
        stake_tx_hash: Optional[str] = None
    ) -> Commitment:
        """Create a new commitment"""

        end_date = datetime.utcnow() + timedelta(days=duration_days)

        commitment = Commitment(
            user_id=user_id,
            pod_id=pod_id,
            commitment_type=commitment_type,
            status=CommitmentStatus.ACTIVE,
            stake_amount=stake_amount,
            target_value=target_value,
            current_progress=0,
            start_date=datetime.utcnow(),
            end_date=end_date,
            contract_address=contract_address,
            stake_tx_hash=stake_tx_hash
        )

        db.add(commitment)
        db.commit()
        db.refresh(commitment)

        # Record transaction
        if stake_tx_hash:
            StakingService.record_transaction(
                db=db,
                user_id=user_id,
                commitment_id=commitment.id,
                pod_id=pod_id,
                transaction_type=TransactionType.STAKE,
                transaction_hash=stake_tx_hash,
                contract_address=contract_address or "",
                amount=stake_amount
            )

        return commitment

    @staticmethod
    def get_user_commitments(
        db: Session,
        user_id: int,
        status: Optional[CommitmentStatus] = None
    ) -> List[Commitment]:
        """Get all commitments for a user"""
        query = db.query(Commitment).filter(Commitment.user_id == user_id)

        if status:
            query = query.filter(Commitment.status == status)

        return query.order_by(Commitment.created_at.desc()).all()

    @staticmethod
    def get_commitment(db: Session, commitment_id: int) -> Optional[Commitment]:
        """Get a specific commitment"""
        return db.query(Commitment).filter(Commitment.id == commitment_id).first()

    @staticmethod
    def update_commitment_progress(
        db: Session,
        commitment_id: int,
        progress: int,
        attestation_hash: str,
        signature: str
    ) -> Commitment:
        """Update commitment progress with attestation"""
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()

        if not commitment:
            raise ValueError("Commitment not found")

        if commitment.status != CommitmentStatus.ACTIVE:
            raise ValueError("Commitment is not active")

        commitment.current_progress = progress

        # Check if commitment is completed
        if progress >= commitment.target_value:
            commitment.status = CommitmentStatus.COMPLETED
            commitment.completed_at = datetime.utcnow()

            # Calculate reward
            web3_service = get_web3_service()
            reward_multiplier = Decimal("1.10")  # 10% bonus
            commitment.reward_amount = commitment.stake_amount * reward_multiplier

        db.commit()
        db.refresh(commitment)

        return commitment

    @staticmethod
    def claim_commitment_reward(
        db: Session,
        commitment_id: int,
        claim_tx_hash: str
    ) -> Commitment:
        """Mark commitment as claimed"""
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()

        if not commitment:
            raise ValueError("Commitment not found")

        if commitment.status != CommitmentStatus.COMPLETED:
            raise ValueError("Commitment is not completed")

        if commitment.claimed_at:
            raise ValueError("Reward already claimed")

        commitment.status = CommitmentStatus.CLAIMED
        commitment.claimed_at = datetime.utcnow()
        commitment.claim_tx_hash = claim_tx_hash

        db.commit()
        db.refresh(commitment)

        # Record transaction
        StakingService.record_transaction(
            db=db,
            user_id=commitment.user_id,
            commitment_id=commitment.id,
            transaction_type=TransactionType.REWARD,
            transaction_hash=claim_tx_hash,
            contract_address=commitment.contract_address or "",
            amount=commitment.reward_amount or commitment.stake_amount
        )

        return commitment

    @staticmethod
    def fail_commitment(
        db: Session,
        commitment_id: int,
        penalty_tx_hash: str
    ) -> Commitment:
        """Mark commitment as failed and record penalty"""
        commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()

        if not commitment:
            raise ValueError("Commitment not found")

        if commitment.status != CommitmentStatus.ACTIVE:
            raise ValueError("Commitment is not active")

        if datetime.utcnow() <= commitment.end_date:
            raise ValueError("Commitment deadline has not passed")

        commitment.status = CommitmentStatus.FAILED
        commitment.penalty_amount = commitment.stake_amount

        db.commit()
        db.refresh(commitment)

        # Update scholarship pool
        StakingService.add_to_scholarship_pool(db, commitment.stake_amount)

        # Record transaction
        StakingService.record_transaction(
            db=db,
            user_id=commitment.user_id,
            commitment_id=commitment.id,
            transaction_type=TransactionType.PENALTY,
            transaction_hash=penalty_tx_hash,
            contract_address=commitment.contract_address or "",
            amount=commitment.stake_amount
        )

        return commitment

    @staticmethod
    def check_expired_commitments(db: Session) -> List[Commitment]:
        """
        Check for expired commitments that should be failed
        Returns list of commitments that need to be failed on-chain
        """
        now = datetime.utcnow()

        expired_commitments = db.query(Commitment).filter(
            and_(
                Commitment.status == CommitmentStatus.ACTIVE,
                Commitment.end_date < now
            )
        ).all()

        return expired_commitments

    # ============ Pod Methods ============

    @staticmethod
    def create_pod(
        db: Session,
        name: str,
        description: str,
        commitment_type: CommitmentType,
        target_value: int,
        stake_amount: Decimal,
        duration_days: int,
        created_by: int,
        max_members: int = 10,
        min_members: int = 2,
        contract_address: Optional[str] = None
    ) -> Pod:
        """Create a new accountability pod"""

        end_date = datetime.utcnow() + timedelta(days=duration_days)

        pod = Pod(
            name=name,
            description=description,
            commitment_type=commitment_type,
            target_value=target_value,
            stake_amount=stake_amount,
            max_members=max_members,
            min_members=min_members,
            status=PodStatus.OPEN,
            end_date=end_date,
            contract_address=contract_address,
            created_by=created_by
        )

        db.add(pod)
        db.commit()
        db.refresh(pod)

        return pod

    @staticmethod
    def get_pod(db: Session, pod_id: int) -> Optional[Pod]:
        """Get a specific pod"""
        return db.query(Pod).filter(Pod.id == pod_id).first()

    @staticmethod
    def get_open_pods(db: Session) -> List[Pod]:
        """Get all open pods that can be joined"""
        return db.query(Pod).filter(
            Pod.status == PodStatus.OPEN
        ).order_by(Pod.created_at.desc()).all()

    @staticmethod
    def join_pod(
        db: Session,
        pod_id: int,
        user_id: int,
        commitment_id: int
    ) -> PodMembership:
        """Add a user to a pod"""
        pod = db.query(Pod).filter(Pod.id == pod_id).first()

        if not pod:
            raise ValueError("Pod not found")

        if pod.status != PodStatus.OPEN:
            raise ValueError("Pod is not open for new members")

        if pod.total_members >= pod.max_members:
            raise ValueError("Pod is full")

        # Check if user is already in pod
        existing = db.query(PodMembership).filter(
            and_(
                PodMembership.pod_id == pod_id,
                PodMembership.user_id == user_id
            )
        ).first()

        if existing:
            raise ValueError("User already in pod")

        membership = PodMembership(
            user_id=user_id,
            pod_id=pod_id,
            commitment_id=commitment_id,
            is_active=True
        )

        db.add(membership)

        # Update pod stats
        pod.total_members += 1
        pod.total_staked += pod.stake_amount

        db.commit()
        db.refresh(membership)

        return membership

    @staticmethod
    def start_pod(db: Session, pod_id: int) -> Pod:
        """Start a pod (lock it from new members)"""
        pod = db.query(Pod).filter(Pod.id == pod_id).first()

        if not pod:
            raise ValueError("Pod not found")

        if pod.status != PodStatus.OPEN:
            raise ValueError("Pod is not open")

        if pod.total_members < pod.min_members:
            raise ValueError(f"Pod needs at least {pod.min_members} members")

        pod.status = PodStatus.ACTIVE
        pod.start_date = datetime.utcnow()

        db.commit()
        db.refresh(pod)

        return pod

    @staticmethod
    def get_pod_members(db: Session, pod_id: int) -> List[Dict[str, Any]]:
        """Get all members of a pod with their progress"""
        memberships = db.query(PodMembership).filter(
            PodMembership.pod_id == pod_id
        ).all()

        members = []
        for membership in memberships:
            user = db.query(User).filter(User.id == membership.user_id).first()
            commitment = None
            if membership.commitment_id:
                commitment = db.query(Commitment).filter(
                    Commitment.id == membership.commitment_id
                ).first()

            members.append({
                "user_id": membership.user_id,
                "username": user.name if user else "Unknown",
                "email": user.email if user else "",
                "current_progress": membership.current_progress,
                "is_active": membership.is_active,
                "has_completed": membership.has_completed,
                "commitment": {
                    "id": commitment.id if commitment else None,
                    "current_progress": commitment.current_progress if commitment else 0,
                    "target_value": commitment.target_value if commitment else 0,
                    "status": commitment.status if commitment else None
                } if commitment else None
            })

        return members

    # ============ Transaction Methods ============

    @staticmethod
    def record_transaction(
        db: Session,
        user_id: int,
        transaction_type: TransactionType,
        transaction_hash: str,
        contract_address: str,
        amount: Decimal,
        commitment_id: Optional[int] = None,
        pod_id: Optional[int] = None,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None
    ) -> StakingTransaction:
        """Record a blockchain transaction"""

        transaction = StakingTransaction(
            user_id=user_id,
            commitment_id=commitment_id,
            pod_id=pod_id,
            transaction_type=transaction_type,
            transaction_hash=transaction_hash,
            contract_address=contract_address,
            amount=amount,
            status="pending",
            from_address=from_address,
            to_address=to_address
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    @staticmethod
    def update_transaction_status(
        db: Session,
        transaction_hash: str,
        status: str,
        block_number: Optional[int] = None
    ) -> Optional[StakingTransaction]:
        """Update transaction status"""
        transaction = db.query(StakingTransaction).filter(
            StakingTransaction.transaction_hash == transaction_hash
        ).first()

        if transaction:
            transaction.status = status
            if block_number:
                transaction.block_number = block_number
            if status == "confirmed":
                transaction.confirmed_at = datetime.utcnow()

            db.commit()
            db.refresh(transaction)

        return transaction

    @staticmethod
    def get_user_transactions(
        db: Session,
        user_id: int,
        limit: int = 50
    ) -> List[StakingTransaction]:
        """Get user's transaction history"""
        return db.query(StakingTransaction).filter(
            StakingTransaction.user_id == user_id
        ).order_by(StakingTransaction.created_at.desc()).limit(limit).all()

    # ============ Attestation Methods ============

    @staticmethod
    def create_attestation(
        db: Session,
        commitment_id: int,
        user_id: int,
        progress_value: int,
        activity_type: str,
        activity_ids: List[int],
        signature: str,
        signature_hash: str,
        attestation_hash: str
    ) -> MilestoneAttestation:
        """Create a milestone attestation"""

        attestation = MilestoneAttestation(
            commitment_id=commitment_id,
            user_id=user_id,
            milestone_date=datetime.utcnow(),
            progress_value=progress_value,
            is_valid=True,
            activity_type=activity_type,
            activity_ids=str(activity_ids),
            signature=signature,
            signature_hash=signature_hash,
            extra_data=f'{{"attestation_hash": "{attestation_hash}"}}'
        )

        db.add(attestation)
        db.commit()
        db.refresh(attestation)

        return attestation

    @staticmethod
    def get_commitment_attestations(
        db: Session,
        commitment_id: int
    ) -> List[MilestoneAttestation]:
        """Get all attestations for a commitment"""
        return db.query(MilestoneAttestation).filter(
            MilestoneAttestation.commitment_id == commitment_id
        ).order_by(MilestoneAttestation.created_at.desc()).all()

    # ============ Scholarship Pool Methods ============

    @staticmethod
    def get_scholarship_pool(db: Session) -> ScholarshipPool:
        """Get scholarship pool stats"""
        pool = db.query(ScholarshipPool).first()

        if not pool:
            # Create initial pool
            pool = ScholarshipPool(
                total_contributed=Decimal("0"),
                total_distributed=Decimal("0"),
                current_balance=Decimal("0")
            )
            db.add(pool)
            db.commit()
            db.refresh(pool)

        return pool

    @staticmethod
    def add_to_scholarship_pool(db: Session, amount: Decimal) -> ScholarshipPool:
        """Add funds to scholarship pool"""
        pool = StakingService.get_scholarship_pool(db)

        pool.total_contributed += amount
        pool.current_balance += amount
        pool.total_failed_commitments += 1
        pool.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(pool)

        return pool


# Singleton accessor
def get_staking_service() -> StakingService:
    """Get staking service"""
    return StakingService()
