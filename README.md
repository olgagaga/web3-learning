# Web3 Education Platform

An AI-guided IELTS/TOEFL test preparation platform with Web3 commitment staking, gamification, and blockchain-verified achievements.

**For detailed project status and deployment instructions, see [PROJECT_STATUS.md](PROJECT_STATUS.md)**

## Quick Overview

### Working Features
- ✅ **Adaptive Reading Practice** - 18 questions, instant feedback
- ✅ **AI Writing Coach** - Gemini-powered essay scoring
- ✅ **Quests & Badges** - Gamification with automatic achievement tracking
- ✅ **Progress Analytics** - Detailed learning statistics

### In Progress (Priority)
- 🟡 **Web3 Commitment Staking** - Stake tokens on learning goals (backend complete, needs deployment)
- 🟡 **Accountability Pods** - Team-based commitments (backend complete, needs deployment)

## Tech Stack

### Frontend
- React 18 with Vite
- React Router for navigation
- Tailwind CSS with Claude orange palette
- Zustand for state management
- Axios for API calls

### Backend
- FastAPI (Python)
- PostgreSQL database
- SQLAlchemy ORM
- JWT authentication
- Gemini AI integration

## Project Structure

```
web3-edu-platform/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   │   ├── auth/      # Authentication components
│   │   │   └── layout/    # Layout components (Sidebar, Header)
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── stores/        # Zustand stores
│   │   └── styles/        # CSS files
│   └── public/
└── server/                # Python backend
    ├── app/
    │   ├── api/           # API routes and schemas
    │   ├── models/        # Database models
    │   ├── services/      # Business logic
    │   ├── config/        # Configuration
    │   └── middleware/    # Custom middleware
    └── database/          # Database schema and migrations
```

## Quick Start

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed setup instructions.

### TL;DR

```bash
# 1. Database
sudo -u postgres psql -c "CREATE DATABASE web3_edu_platform;"
sudo -u postgres psql -d web3_edu_platform -f server/database/schema.sql

# 2. Backend
cd server && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your config
python -m database.seed_reading_data
python -m database.seed_writing_data
python -m database.seed_quest_data
python main.py  # Runs on http://localhost:8001

# 3. Frontend
cd client
npm install --legacy-peer-deps
cp .env.example .env  # Edit with your config
npm run dev  # Runs on http://localhost:3000

# 4. Deploy Contract (Priority)
npx thirdweb deploy contracts/CommitmentStaking.sol
# See contracts/README.md for details
```

## Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current status, priorities, and deployment guide
- **[STATUS.md](STATUS.md)** - Detailed Web3 staking feature status
- **[READING_MODULE.md](READING_MODULE.md)** - Reading practice documentation
- **[WRITING_MODULE.md](WRITING_MODULE.md)** - Writing coach documentation
- **[BADGES_MODULE.md](BADGES_MODULE.md)** - Badges system documentation
- **[contracts/README.md](contracts/README.md)** - Smart contract deployment guide

## Key API Endpoints

Full API documentation available at: http://localhost:8001/docs (when backend is running)

**Core Features:**
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/reading/next` - Get next reading item
- `POST /api/reading/submit` - Submit answer
- `POST /api/writing/submit` - Submit essay
- `GET /api/quests/active` - Get active quests
- `GET /api/quests/badges` - Get user badges

**Web3 Staking (Priority):**
- `POST /api/staking/wallet/connect` - Connect wallet
- `POST /api/staking/commitments` - Create commitment
- `GET /api/staking/commitments` - List commitments
- `POST /api/staking/commitments/{id}/attest` - Generate attestation
- `POST /api/staking/commitments/{id}/claim` - Claim reward
- `GET /api/staking/dashboard` - User dashboard

## Current Priority

**Deploy smart contracts and test web3 features**

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for:
- Step-by-step deployment instructions
- Testing guide
- Troubleshooting tips
- Environment configuration

## Resources

- **Thirdweb Dashboard:** https://thirdweb.com/dashboard
- **Sepolia Faucet:** https://sepoliafaucet.com/ or https://faucet.sepolia.dev/
- **Sepolia Explorer:** https://sepolia.etherscan.io/
- **API Documentation:** http://localhost:8001/docs

## License

MIT
