-- Migration: Add staking and accountability pods tables
-- Date: 2025-11-11
-- Description: Adds Web3 staking, pods, attestations, and scholarship pool functionality

-- Wallets table for Web3 interactions
CREATE TABLE IF NOT EXISTS wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    wallet_provider VARCHAR(50) NOT NULL,
    is_custodial BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE,
    provider_user_id VARCHAR(255),
    extra_data TEXT
);

-- Pods table for accountability groups
CREATE TABLE IF NOT EXISTS pods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    commitment_type VARCHAR(50) NOT NULL,
    target_value INTEGER NOT NULL,
    stake_amount NUMERIC(18, 6) NOT NULL,
    max_members INTEGER DEFAULT 10,
    min_members INTEGER DEFAULT 2,
    status VARCHAR(50) DEFAULT 'open' NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    contract_address VARCHAR(42),
    total_staked NUMERIC(18, 6) DEFAULT 0,
    total_members INTEGER DEFAULT 0,
    successful_members INTEGER DEFAULT 0,
    failed_members INTEGER DEFAULT 0,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Commitments table for individual stakes
CREATE TABLE IF NOT EXISTS commitments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pod_id INTEGER REFERENCES pods(id) ON DELETE SET NULL,
    commitment_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    stake_amount NUMERIC(18, 6) NOT NULL,
    target_value INTEGER NOT NULL,
    current_progress INTEGER DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    claimed_at TIMESTAMP WITH TIME ZONE,
    contract_address VARCHAR(42),
    stake_tx_hash VARCHAR(66),
    claim_tx_hash VARCHAR(66),
    reward_amount NUMERIC(18, 6),
    penalty_amount NUMERIC(18, 6),
    description TEXT,
    extra_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Pod memberships table (many-to-many)
CREATE TABLE IF NOT EXISTS pod_memberships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pod_id INTEGER NOT NULL REFERENCES pods(id) ON DELETE CASCADE,
    commitment_id INTEGER REFERENCES commitments(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    has_completed BOOLEAN DEFAULT FALSE,
    current_progress INTEGER DEFAULT 0,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, pod_id)
);

-- Staking transactions table
CREATE TABLE IF NOT EXISTS staking_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    commitment_id INTEGER REFERENCES commitments(id) ON DELETE SET NULL,
    pod_id INTEGER REFERENCES pods(id) ON DELETE SET NULL,
    transaction_type VARCHAR(50) NOT NULL,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    contract_address VARCHAR(42) NOT NULL,
    amount NUMERIC(18, 6) NOT NULL,
    gas_fee NUMERIC(18, 6),
    status VARCHAR(20) DEFAULT 'pending',
    block_number INTEGER,
    from_address VARCHAR(42),
    to_address VARCHAR(42),
    extra_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP WITH TIME ZONE
);

-- Milestone attestations table
CREATE TABLE IF NOT EXISTS milestone_attestations (
    id SERIAL PRIMARY KEY,
    commitment_id INTEGER NOT NULL REFERENCES commitments(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    milestone_date TIMESTAMP WITH TIME ZONE NOT NULL,
    progress_value INTEGER NOT NULL,
    is_valid BOOLEAN DEFAULT TRUE,
    activity_type VARCHAR(50),
    activity_ids TEXT,
    signature VARCHAR(132),
    signature_hash VARCHAR(66),
    extra_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP WITH TIME ZONE
);

-- Scholarship pool table
CREATE TABLE IF NOT EXISTS scholarship_pool (
    id SERIAL PRIMARY KEY,
    total_contributed NUMERIC(18, 6) DEFAULT 0,
    total_distributed NUMERIC(18, 6) DEFAULT 0,
    current_balance NUMERIC(18, 6) DEFAULT 0,
    pool_address VARCHAR(42),
    contract_address VARCHAR(42),
    total_failed_commitments INTEGER DEFAULT 0,
    total_scholarships_awarded INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scholarship distributions table
CREATE TABLE IF NOT EXISTS scholarship_distributions (
    id SERIAL PRIMARY KEY,
    recipient_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    amount NUMERIC(18, 6) NOT NULL,
    reason TEXT,
    transaction_hash VARCHAR(66) UNIQUE,
    contract_address VARCHAR(42),
    status VARCHAR(20) DEFAULT 'pending',
    distributed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_wallets_user ON wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_wallets_address ON wallets(wallet_address);

CREATE INDEX IF NOT EXISTS idx_commitments_user ON commitments(user_id);
CREATE INDEX IF NOT EXISTS idx_commitments_status ON commitments(status);
CREATE INDEX IF NOT EXISTS idx_commitments_pod ON commitments(pod_id);

CREATE INDEX IF NOT EXISTS idx_pods_status ON pods(status);
CREATE INDEX IF NOT EXISTS idx_pods_creator ON pods(created_by);

CREATE INDEX IF NOT EXISTS idx_pod_memberships_user ON pod_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_pod_memberships_pod ON pod_memberships(pod_id);

CREATE INDEX IF NOT EXISTS idx_staking_tx_user ON staking_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_staking_tx_hash ON staking_transactions(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_staking_tx_commitment ON staking_transactions(commitment_id);

CREATE INDEX IF NOT EXISTS idx_attestations_commitment ON milestone_attestations(commitment_id);
CREATE INDEX IF NOT EXISTS idx_attestations_user ON milestone_attestations(user_id);

CREATE INDEX IF NOT EXISTS idx_scholarship_dist_user ON scholarship_distributions(recipient_user_id);
CREATE INDEX IF NOT EXISTS idx_scholarship_dist_tx ON scholarship_distributions(transaction_hash);

-- Insert initial scholarship pool record
INSERT INTO scholarship_pool (total_contributed, total_distributed, current_balance)
VALUES (0, 0, 0)
ON CONFLICT DO NOTHING;
