"""
API routes for staking, commitments, pods, and Web3 operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.user import User
from app.models.staking import Wallet, CommitmentType, CommitmentStatus
from app.api.schemas.staking import (
    WalletConnectRequest,
    WalletResponse,
    CreateCommitmentRequest,
    CommitmentResponse,
    CommitmentProgressResponse,
    AttestationResponse,
    ClaimRewardRequest,
    CreatePodRequest,
    JoinPodRequest,
    PodResponse,
    PodDetailResponse,
    TransactionResponse,
    UpdateTransactionStatusRequest,
    ScholarshipPoolResponse,
    StakingDashboardResponse,
    CommitmentSummaryResponse
)
from app.services.auth import get_current_active_user
from app.services.staking_service import StakingService, get_staking_service
from app.services.attestation_service import AttestationService, get_attestation_service
from app.services.web3_service import get_web3_service
from decimal import Decimal

router = APIRouter(prefix="/staking", tags=["Staking & Web3"])


# ============ Wallet Endpoints ============

@router.post("/wallet/connect", response_model=WalletResponse)
async def connect_wallet(
    wallet_data: WalletConnectRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Connect or update user's Web3 wallet"""

    # Check if wallet already exists
    existing_wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()

    if existing_wallet:
        # Update existing wallet
        existing_wallet.wallet_address = wallet_data.wallet_address
        existing_wallet.wallet_provider = wallet_data.wallet_provider
        existing_wallet.provider_user_id = wallet_data.provider_user_id
        existing_wallet.last_activity = None  # Will be updated by database

        db.commit()
        db.refresh(existing_wallet)
        wallet = existing_wallet
    else:
        # Create new wallet
        wallet = Wallet(
            user_id=current_user.id,
            wallet_address=wallet_data.wallet_address,
            wallet_provider=wallet_data.wallet_provider,
            is_custodial=True,
            provider_user_id=wallet_data.provider_user_id
        )

        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    # Get balance
    web3_service = get_web3_service()
    balance = web3_service.get_balance(wallet.wallet_address)

    response = WalletResponse.from_orm(wallet)
    response.balance = str(balance)

    return response


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's connected wallet"""

    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No wallet connected"
        )

    # Get balance
    web3_service = get_web3_service()
    balance = web3_service.get_balance(wallet.wallet_address)

    response = WalletResponse.from_orm(wallet)
    response.balance = str(balance)

    return response


# ============ Commitment Endpoints ============

@router.post("/commitments", response_model=CommitmentResponse, status_code=status.HTTP_201_CREATED)
async def create_commitment(
    commitment_data: CreateCommitmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new commitment (call this after blockchain stake transaction)"""

    # Verify user has wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect a wallet first"
        )

    # Create commitment
    staking_service = get_staking_service()

    commitment = staking_service.create_commitment(
        db=db,
        user_id=current_user.id,
        commitment_type=CommitmentType(commitment_data.commitment_type),
        target_value=commitment_data.target_value,
        duration_days=commitment_data.duration_days,
        stake_amount=Decimal(commitment_data.stake_amount)
    )

    return CommitmentResponse.from_orm(commitment)


@router.get("/commitments", response_model=List[CommitmentResponse])
async def get_my_commitments(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all commitments for current user"""

    staking_service = get_staking_service()

    status_enum = CommitmentStatus(status_filter) if status_filter else None
    commitments = staking_service.get_user_commitments(db, current_user.id, status_enum)

    return [CommitmentResponse.from_orm(c) for c in commitments]


@router.get("/commitments/{commitment_id}", response_model=CommitmentResponse)
async def get_commitment(
    commitment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific commitment"""

    staking_service = get_staking_service()
    commitment = staking_service.get_commitment(db, commitment_id)

    if not commitment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commitment not found"
        )

    if commitment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this commitment"
        )

    return CommitmentResponse.from_orm(commitment)


@router.get("/commitments/{commitment_id}/progress", response_model=CommitmentProgressResponse)
async def check_commitment_progress(
    commitment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check current progress for a commitment"""

    # Verify commitment belongs to user
    staking_service = get_staking_service()
    commitment = staking_service.get_commitment(db, commitment_id)

    if not commitment or commitment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commitment not found"
        )

    # Get progress
    attestation_service = get_attestation_service()
    progress_info = attestation_service.check_commitment_progress(db, commitment_id)

    return CommitmentProgressResponse(**progress_info)


@router.post("/commitments/{commitment_id}/attest", response_model=AttestationResponse)
async def generate_attestation(
    commitment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a signed attestation for commitment progress"""

    # Verify commitment belongs to user
    staking_service = get_staking_service()
    commitment = staking_service.get_commitment(db, commitment_id)

    if not commitment or commitment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commitment not found"
        )

    # Generate attestation
    attestation_service = get_attestation_service()

    try:
        attestation = attestation_service.generate_attestation_for_commitment(db, commitment_id)

        if not attestation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No progress update available. Keep learning!"
            )

        return AttestationResponse(**attestation)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/commitments/{commitment_id}/claim")
async def claim_reward(
    commitment_id: int,
    claim_data: ClaimRewardRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record successful reward claim"""

    staking_service = get_staking_service()

    try:
        commitment = staking_service.claim_commitment_reward(
            db=db,
            commitment_id=commitment_id,
            claim_tx_hash=claim_data.transaction_hash
        )

        return {
            "success": True,
            "message": "Reward claimed successfully",
            "commitment": CommitmentResponse.from_orm(commitment)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/commitments/{commitment_id}/summary", response_model=CommitmentSummaryResponse)
async def get_commitment_summary(
    commitment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive commitment summary with daily activity"""

    # Verify commitment belongs to user
    staking_service = get_staking_service()
    commitment = staking_service.get_commitment(db, commitment_id)

    if not commitment or commitment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commitment not found"
        )

    attestation_service = get_attestation_service()
    summary = attestation_service.get_commitment_summary(db, commitment_id)

    return CommitmentSummaryResponse(**summary)


# ============ Pod Endpoints ============

@router.post("/pods", response_model=PodResponse, status_code=status.HTTP_201_CREATED)
async def create_pod(
    pod_data: CreatePodRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new accountability pod"""

    staking_service = get_staking_service()

    pod = staking_service.create_pod(
        db=db,
        name=pod_data.name,
        description=pod_data.description,
        commitment_type=CommitmentType(pod_data.commitment_type),
        target_value=pod_data.target_value,
        stake_amount=Decimal(pod_data.stake_amount),
        duration_days=pod_data.duration_days,
        created_by=current_user.id,
        max_members=pod_data.max_members,
        min_members=pod_data.min_members
    )

    return PodResponse.from_orm(pod)


@router.get("/pods", response_model=List[PodResponse])
async def get_open_pods(
    db: Session = Depends(get_db)
):
    """Get all open pods available to join"""

    staking_service = get_staking_service()
    pods = staking_service.get_open_pods(db)

    return [PodResponse.from_orm(p) for p in pods]


@router.get("/pods/{pod_id}", response_model=PodDetailResponse)
async def get_pod(
    pod_id: int,
    db: Session = Depends(get_db)
):
    """Get pod details with member list"""

    staking_service = get_staking_service()
    pod = staking_service.get_pod(db, pod_id)

    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pod not found"
        )

    members = staking_service.get_pod_members(db, pod_id)

    pod_response = PodResponse.from_orm(pod)
    return PodDetailResponse(**pod_response.dict(), members=members)


@router.post("/pods/{pod_id}/join", response_model=CommitmentResponse)
async def join_pod(
    pod_id: int,
    join_data: JoinPodRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join an accountability pod (call after blockchain stake)"""

    # Verify user has wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect a wallet first"
        )

    staking_service = get_staking_service()

    # Get pod details
    pod = staking_service.get_pod(db, pod_id)
    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pod not found"
        )

    # Create commitment for pod member
    commitment = staking_service.create_commitment(
        db=db,
        user_id=current_user.id,
        commitment_type=pod.commitment_type,
        target_value=pod.target_value,
        duration_days=(pod.end_date - pod.created_at).days if pod.end_date else 7,
        stake_amount=pod.stake_amount,
        pod_id=pod_id,
        stake_tx_hash=join_data.transaction_hash
    )

    # Add user to pod
    try:
        staking_service.join_pod(
            db=db,
            pod_id=pod_id,
            user_id=current_user.id,
            commitment_id=commitment.id
        )
    except ValueError as e:
        # Rollback commitment if join fails
        db.delete(commitment)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return CommitmentResponse.from_orm(commitment)


@router.post("/pods/{pod_id}/start")
async def start_pod(
    pod_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a pod (only creator can start)"""

    staking_service = get_staking_service()
    pod = staking_service.get_pod(db, pod_id)

    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pod not found"
        )

    if pod.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only pod creator can start the pod"
        )

    try:
        pod = staking_service.start_pod(db, pod_id)
        return {
            "success": True,
            "message": "Pod started successfully",
            "pod": PodResponse.from_orm(pod)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============ Transaction Endpoints ============

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_my_transactions(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's transaction history"""

    staking_service = get_staking_service()
    transactions = staking_service.get_user_transactions(db, current_user.id, limit)

    return [TransactionResponse.from_orm(t) for t in transactions]


@router.post("/transactions/update-status")
async def update_transaction_status(
    update_data: UpdateTransactionStatusRequest,
    db: Session = Depends(get_db)
):
    """Update transaction status (for webhook/polling)"""

    staking_service = get_staking_service()

    transaction = staking_service.update_transaction_status(
        db=db,
        transaction_hash=update_data.transaction_hash,
        status=update_data.status,
        block_number=update_data.block_number
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return {
        "success": True,
        "transaction": TransactionResponse.from_orm(transaction)
    }


# ============ Scholarship Pool Endpoints ============

@router.get("/scholarship-pool", response_model=ScholarshipPoolResponse)
async def get_scholarship_pool(
    db: Session = Depends(get_db)
):
    """Get scholarship pool statistics"""

    staking_service = get_staking_service()
    pool = staking_service.get_scholarship_pool(db)

    return ScholarshipPoolResponse.from_orm(pool)


# ============ Dashboard/Stats Endpoints ============

@router.get("/dashboard", response_model=StakingDashboardResponse)
async def get_staking_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's staking dashboard statistics"""

    staking_service = get_staking_service()
    commitments = staking_service.get_user_commitments(db, current_user.id)

    total = len(commitments)
    active = len([c for c in commitments if c.status == CommitmentStatus.ACTIVE])
    completed = len([c for c in commitments if c.status == CommitmentStatus.COMPLETED or c.status == CommitmentStatus.CLAIMED])
    failed = len([c for c in commitments if c.status == CommitmentStatus.FAILED])

    total_staked = sum([c.stake_amount for c in commitments if c.status in [CommitmentStatus.ACTIVE, CommitmentStatus.COMPLETED]])
    total_rewards = sum([c.reward_amount for c in commitments if c.reward_amount and c.status == CommitmentStatus.CLAIMED])

    success_rate = (completed / total * 100) if total > 0 else 0.0

    return StakingDashboardResponse(
        total_commitments=total,
        active_commitments=active,
        completed_commitments=completed,
        failed_commitments=failed,
        total_staked=str(total_staked),
        total_rewards_earned=str(total_rewards or 0),
        active_pods=0,  # TODO: Calculate active pods
        success_rate=success_rate,
        current_streak=current_user.current_streak
    )
