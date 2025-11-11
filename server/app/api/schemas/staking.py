"""
Pydantic schemas for staking and Web3 API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


# ============ Enums ============

class CommitmentTypeSchema(str, Enum):
    STREAK_7_DAY = "streak_7_day"
    STREAK_30_DAY = "streak_30_day"
    READING_GOAL = "reading_goal"
    WRITING_GOAL = "writing_goal"
    CUSTOM = "custom"


class CommitmentStatusSchema(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CLAIMED = "claimed"
    REFUNDED = "refunded"


class PodStatusSchema(str, Enum):
    OPEN = "open"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


# ============ Wallet Schemas ============

class WalletConnectRequest(BaseModel):
    wallet_address: str = Field(..., description="Ethereum wallet address")
    wallet_provider: str = Field(..., description="Wallet provider (thirdweb, metamask, etc.)")
    provider_user_id: Optional[str] = Field(None, description="External provider user ID")

    @validator('wallet_address')
    def validate_address(cls, v):
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid Ethereum address format')
        return v.lower()


class WalletResponse(BaseModel):
    id: int
    user_id: int
    wallet_address: str
    wallet_provider: str
    is_custodial: bool
    created_at: datetime
    balance: Optional[str] = None

    class Config:
        from_attributes = True


# ============ Commitment Schemas ============

class CreateCommitmentRequest(BaseModel):
    commitment_type: CommitmentTypeSchema
    target_value: int = Field(..., gt=0, description="Target value (e.g., 7 for 7-day streak)")
    duration_days: int = Field(..., gt=0, le=365, description="Duration in days")
    stake_amount: str = Field(..., description="Stake amount in MATIC (0.01-1.0)")

    @validator('stake_amount')
    def validate_stake(cls, v):
        amount = Decimal(v)
        if amount < Decimal("0.01") or amount > Decimal("1.0"):
            raise ValueError('Stake amount must be between 0.01 and 1.0')
        return v


class CommitmentResponse(BaseModel):
    id: int
    user_id: int
    pod_id: Optional[int]
    commitment_type: str
    status: str
    stake_amount: str
    target_value: int
    current_progress: int
    start_date: datetime
    end_date: datetime
    completed_at: Optional[datetime]
    claimed_at: Optional[datetime]
    contract_address: Optional[str]
    stake_tx_hash: Optional[str]
    claim_tx_hash: Optional[str]
    reward_amount: Optional[str]
    penalty_amount: Optional[str]
    created_at: datetime

    @validator('stake_amount', 'reward_amount', 'penalty_amount', pre=True)
    def decimal_to_str(cls, v):
        return str(v) if v is not None else None

    class Config:
        from_attributes = True


class CommitmentProgressResponse(BaseModel):
    commitment_id: int
    status: str
    stored_progress: int
    actual_progress: int
    target_value: int
    needs_attestation: bool
    is_completed: bool


class AttestationResponse(BaseModel):
    commitment_id: int
    progress: int
    target_value: int
    attestation_hash: str
    signature: str
    message_hash: str
    signer: str
    attestation_id: int
    is_completed: bool


class ClaimRewardRequest(BaseModel):
    commitment_id: int
    transaction_hash: str = Field(..., description="Blockchain transaction hash")


# ============ Pod Schemas ============

class CreatePodRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    commitment_type: CommitmentTypeSchema
    target_value: int = Field(..., gt=0)
    stake_amount: str = Field(..., description="Required stake per member (0.01-1.0 MATIC)")
    duration_days: int = Field(..., gt=0, le=365)
    max_members: int = Field(default=10, ge=2, le=50)
    min_members: int = Field(default=2, ge=2)

    @validator('stake_amount')
    def validate_stake(cls, v):
        amount = Decimal(v)
        if amount < Decimal("0.01") or amount > Decimal("1.0"):
            raise ValueError('Stake amount must be between 0.01 and 1.0')
        return v

    @validator('min_members')
    def validate_min_members(cls, v, values):
        if 'max_members' in values and v > values['max_members']:
            raise ValueError('min_members cannot be greater than max_members')
        return v


class JoinPodRequest(BaseModel):
    pod_id: int
    transaction_hash: str = Field(..., description="Blockchain transaction hash for stake")


class PodResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    commitment_type: str
    target_value: int
    stake_amount: str
    max_members: int
    min_members: int
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    contract_address: Optional[str]
    total_staked: str
    total_members: int
    successful_members: int
    failed_members: int
    created_by: Optional[int]
    created_at: datetime

    @validator('stake_amount', 'total_staked', pre=True)
    def decimal_to_str(cls, v):
        return str(v) if v is not None else None

    class Config:
        from_attributes = True


class PodMemberResponse(BaseModel):
    user_id: int
    username: str
    email: str
    current_progress: int
    is_active: bool
    has_completed: bool
    commitment: Optional[dict]


class PodDetailResponse(PodResponse):
    members: List[PodMemberResponse]


# ============ Transaction Schemas ============

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    commitment_id: Optional[int]
    pod_id: Optional[int]
    transaction_type: str
    transaction_hash: str
    contract_address: str
    amount: str
    gas_fee: Optional[str]
    status: str
    block_number: Optional[int]
    from_address: Optional[str]
    to_address: Optional[str]
    created_at: datetime
    confirmed_at: Optional[datetime]

    @validator('amount', 'gas_fee', pre=True)
    def decimal_to_str(cls, v):
        return str(v) if v is not None else None

    class Config:
        from_attributes = True


class UpdateTransactionStatusRequest(BaseModel):
    transaction_hash: str
    status: str = Field(..., pattern="^(pending|confirmed|failed)$")
    block_number: Optional[int] = None


# ============ Scholarship Pool Schemas ============

class ScholarshipPoolResponse(BaseModel):
    total_contributed: str
    total_distributed: str
    current_balance: str
    total_failed_commitments: int
    total_scholarships_awarded: int

    @validator('total_contributed', 'total_distributed', 'current_balance', pre=True)
    def decimal_to_str(cls, v):
        return str(v) if v is not None else None

    class Config:
        from_attributes = True


# ============ Dashboard Schemas ============

class StakingDashboardResponse(BaseModel):
    total_commitments: int
    active_commitments: int
    completed_commitments: int
    failed_commitments: int
    total_staked: str
    total_rewards_earned: str
    active_pods: int
    success_rate: float
    current_streak: int


class CommitmentSummaryResponse(BaseModel):
    commitment: dict
    attestations: List[dict]
    daily_activity: Optional[List[dict]]
    progress_percentage: float
    days_remaining: int


# ============ Attestation Update Request ============

class UpdateProgressRequest(BaseModel):
    """Request to update progress on-chain"""
    commitment_id: int
    progress: int
    attestation_hash: str
    signature: str
    from_address: str
