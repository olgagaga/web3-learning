from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
import enum


class CommitmentType(str, enum.Enum):
    """Types of commitments users can make"""
    STREAK_7_DAY = "streak_7_day"
    STREAK_30_DAY = "streak_30_day"
    READING_GOAL = "reading_goal"
    WRITING_GOAL = "writing_goal"
    CUSTOM = "custom"


class CommitmentStatus(str, enum.Enum):
    """Status of a commitment"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CLAIMED = "claimed"
    REFUNDED = "refunded"


class TransactionType(str, enum.Enum):
    """Types of blockchain transactions"""
    STAKE = "stake"
    REWARD = "reward"
    REFUND = "refund"
    PENALTY = "penalty"
    SCHOLARSHIP = "scholarship"


class PodStatus(str, enum.Enum):
    """Status of an accountability pod"""
    OPEN = "open"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Wallet(Base):
    """User wallet information for Web3 interactions"""
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    wallet_address = Column(String(42), unique=True, nullable=False, index=True)  # Ethereum address
    wallet_provider = Column(String(50), nullable=False)  # thirdweb, web3auth, privy
    is_custodial = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), onupdate=func.now())

    # Metadata
    provider_user_id = Column(String(255))  # External provider's user ID
    extra_data = Column(Text)  # JSON metadata from wallet provider


class Commitment(Base):
    """Individual commitment stakes"""
    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pod_id = Column(Integer, ForeignKey("pods.id", ondelete="SET NULL"), nullable=True)  # Optional pod membership

    # Commitment details
    commitment_type = Column(Enum(CommitmentType), nullable=False)
    status = Column(Enum(CommitmentStatus), default=CommitmentStatus.ACTIVE, nullable=False, index=True)
    stake_amount = Column(Numeric(18, 6), nullable=False)  # Amount in testnet tokens (e.g., 0.01-1.0)

    # Target and progress
    target_value = Column(Integer, nullable=False)  # e.g., 7 for 7-day streak
    current_progress = Column(Integer, default=0)

    # Timing
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)  # Deadline for completion
    completed_at = Column(DateTime(timezone=True))
    claimed_at = Column(DateTime(timezone=True))

    # Blockchain data
    contract_address = Column(String(42))  # Smart contract address
    stake_tx_hash = Column(String(66))  # Transaction hash for initial stake
    claim_tx_hash = Column(String(66))  # Transaction hash for claim/refund

    # Rewards
    reward_amount = Column(Numeric(18, 6))  # Bonus reward if completed
    penalty_amount = Column(Numeric(18, 6))  # Amount sent to scholarship pool if failed

    # Metadata
    description = Column(Text)
    extra_data = Column(Text)  # JSON for additional data

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Pod(Base):
    """Accountability pods for team commitments"""
    __tablename__ = "pods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Pod settings
    commitment_type = Column(Enum(CommitmentType), nullable=False)
    target_value = Column(Integer, nullable=False)  # e.g., 7 for 7-day streak
    stake_amount = Column(Numeric(18, 6), nullable=False)  # Required stake per member
    max_members = Column(Integer, default=10)
    min_members = Column(Integer, default=2)

    # Status
    status = Column(Enum(PodStatus), default=PodStatus.OPEN, nullable=False, index=True)

    # Timing
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    # Blockchain
    contract_address = Column(String(42))

    # Stats
    total_staked = Column(Numeric(18, 6), default=0)
    total_members = Column(Integer, default=0)
    successful_members = Column(Integer, default=0)
    failed_members = Column(Integer, default=0)

    # Creator
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PodMembership(Base):
    """Many-to-many relationship between users and pods"""
    __tablename__ = "pod_memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pod_id = Column(Integer, ForeignKey("pods.id", ondelete="CASCADE"), nullable=False)
    commitment_id = Column(Integer, ForeignKey("commitments.id", ondelete="SET NULL"))

    # Status
    is_active = Column(Boolean, default=True)
    has_completed = Column(Boolean, default=False)

    # Progress tracking
    current_progress = Column(Integer, default=0)

    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Unique constraint: user can only join a pod once
    __table_args__ = (
        {"schema": None},
    )


class StakingTransaction(Base):
    """Blockchain transaction records"""
    __tablename__ = "staking_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id", ondelete="SET NULL"))
    pod_id = Column(Integer, ForeignKey("pods.id", ondelete="SET NULL"))

    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    transaction_hash = Column(String(66), unique=True, nullable=False, index=True)
    contract_address = Column(String(42), nullable=False)

    # Amounts
    amount = Column(Numeric(18, 6), nullable=False)
    gas_fee = Column(Numeric(18, 6))

    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    block_number = Column(Integer)

    # Metadata
    from_address = Column(String(42))
    to_address = Column(String(42))
    extra_data = Column(Text)  # JSON for additional data

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))


class MilestoneAttestation(Base):
    """Backend attestations for milestone completion"""
    __tablename__ = "milestone_attestations"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Attestation details
    milestone_date = Column(DateTime(timezone=True), nullable=False)  # Date of the milestone
    progress_value = Column(Integer, nullable=False)  # Current progress value
    is_valid = Column(Boolean, default=True)

    # Proof data
    activity_type = Column(String(50))  # reading, writing, quest
    activity_ids = Column(Text)  # JSON array of activity IDs as proof

    # Signature
    signature = Column(String(132))  # Backend signature for on-chain verification
    signature_hash = Column(String(66))

    # Metadata
    extra_data = Column(Text)  # JSON for additional proof data

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True))


class ScholarshipPool(Base):
    """Tracks scholarship pool funds from failed commitments"""
    __tablename__ = "scholarship_pool"

    id = Column(Integer, primary_key=True, index=True)

    # Pool stats
    total_contributed = Column(Numeric(18, 6), default=0)
    total_distributed = Column(Numeric(18, 6), default=0)
    current_balance = Column(Numeric(18, 6), default=0)

    # Blockchain
    pool_address = Column(String(42))  # Treasury/pool wallet address
    contract_address = Column(String(42))

    # Stats
    total_failed_commitments = Column(Integer, default=0)
    total_scholarships_awarded = Column(Integer, default=0)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScholarshipDistribution(Base):
    """Records of scholarship distributions from the pool"""
    __tablename__ = "scholarship_distributions"

    id = Column(Integer, primary_key=True, index=True)
    recipient_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Distribution details
    amount = Column(Numeric(18, 6), nullable=False)
    reason = Column(Text)  # Why they received the scholarship

    # Blockchain
    transaction_hash = Column(String(66), unique=True, index=True)
    contract_address = Column(String(42))

    # Status
    status = Column(String(20), default="pending")

    distributed_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
