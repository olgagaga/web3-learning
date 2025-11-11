#!/bin/bash

# Quick Start Script for Web3 Commitment Staking Feature
# Run this after deploying the smart contract and updating .env files

set -e

echo "🚀 Web3 Education Platform - Quick Start"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "DEPLOYMENT_GUIDE.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check backend .env
echo -e "${YELLOW}Checking backend configuration...${NC}"
if [ ! -f "server/.env" ]; then
    echo "❌ server/.env not found"
    exit 1
fi

# Check if contract address is configured
if grep -q "STAKING_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000" server/.env; then
    echo "⚠️  Warning: STAKING_CONTRACT_ADDRESS not configured in server/.env"
    echo "   Please deploy the smart contract first and update the address"
fi

# Check if attestation private key is configured
if grep -q "ATTESTATION_PRIVATE_KEY=your-attestation-private-key-here" server/.env; then
    echo "⚠️  Warning: ATTESTATION_PRIVATE_KEY not configured in server/.env"
    echo "   Please generate a backend wallet and update the private key"
fi

echo -e "${GREEN}✓ Backend .env found${NC}"

# Check frontend .env
echo -e "${YELLOW}Checking frontend configuration...${NC}"
if [ ! -f "client/.env" ]; then
    echo "❌ client/.env not found"
    exit 1
fi

if grep -q "VITE_STAKING_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000" client/.env; then
    echo "⚠️  Warning: VITE_STAKING_CONTRACT_ADDRESS not configured in client/.env"
fi

if grep -q "VITE_THIRDWEB_CLIENT_ID=your-thirdweb-client-id-here" client/.env; then
    echo "⚠️  Warning: VITE_THIRDWEB_CLIENT_ID not configured in client/.env"
    echo "   Get your client ID from https://thirdweb.com/dashboard"
fi

echo -e "${GREEN}✓ Frontend .env found${NC}"
echo ""

# Check PostgreSQL
echo -e "${YELLOW}Checking database connection...${NC}"
if ! command -v psql &> /dev/null; then
    echo "⚠️  Warning: psql command not found. Is PostgreSQL installed?"
else
    if PGPASSWORD=postgres psql -U postgres -d web3_edu_platform -c "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}✓ Database connection successful${NC}"

        # Check if staking tables exist
        if PGPASSWORD=postgres psql -U postgres -d web3_edu_platform -c "\dt wallets" 2>&1 | grep -q "Did not find any relation"; then
            echo "⚠️  Warning: Staking tables not found. Running migration..."
            PGPASSWORD=postgres psql -U postgres -d web3_edu_platform -f server/database/migrations/001_add_staking_tables.sql
            echo -e "${GREEN}✓ Migration completed${NC}"
        else
            echo -e "${GREEN}✓ Staking tables exist${NC}"
        fi
    else
        echo "❌ Could not connect to database. Please check PostgreSQL is running."
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✓ Configuration check complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Deploy smart contract: npx thirdweb deploy contracts/CommitmentStaking.sol"
echo "2. Update STAKING_CONTRACT_ADDRESS in both server/.env and client/.env"
echo "3. Update VITE_THIRDWEB_CLIENT_ID in client/.env"
echo "4. Generate backend wallet and update ATTESTATION_PRIVATE_KEY in server/.env"
echo "5. Start backend: cd server && python main.py"
echo "6. Start frontend: cd client && npm run dev"
echo ""
echo "📚 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo "📝 For feature overview, see WEB3_FEATURE_SUMMARY.md"
echo ""
