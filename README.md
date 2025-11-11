# Web3 Education Platform

An AI-guided microlearning platform for IELTS/TOEFL test preparation with Web3 achievements and gamification.

## Features

- **Adaptive Reading Practice**: Personalized reading comprehension exercises with difficulty adjustment
- **AI Writing Coach**: Essay feedback powered by Gemini AI with rubric-based scoring
- **Gamification**: Quests, streaks, boss challenges, and rewards
- **Web3 Badges**: Verifiable skill credentials as soulbound tokens
- **Progress Analytics**: Detailed tracking of learning progress and skill mastery

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

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+
- Gemini API key

### Database Setup

1. Install PostgreSQL and create a database:

```bash
sudo -u postgres psql
CREATE DATABASE web3_edu_platform;
\q
```

2. Run the schema to create tables:

```bash
sudo -u postgres psql -d web3_edu_platform -f server/database/schema.sql
```

### Backend Setup

1. Navigate to the server directory:

```bash
cd server
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/web3_edu_platform
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
```

6. Seed the practice data:

```bash
# Seed reading practice data (4 passages, 18 questions)
python -m database.seed_reading_data

# Seed writing prompts (8 essay prompts)
python -m database.seed_writing_data
```

7. Start the backend server:

```bash
python main.py
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the client directory:

```bash
cd client
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Available Pages

- **/login** - User login
- **/register** - User registration
- **/dashboard** - Overview and quick actions
- **/reading** - Adaptive reading practice ✅ **Fully Implemented**
- **/writing** - AI-powered writing coach ✅ **Fully Implemented**
- **/quests** - Gamified challenges
- **/badges** - Web3 achievements
- **/progress** - Learning analytics
- **/settings** - User preferences

## Implemented Modules

### ✅ Reading Practice
- 4 passages across difficulty levels (easy, medium, hard)
- 18 comprehension questions with explanations
- Adaptive difficulty algorithm (targets 70-80% success)
- Instant feedback with skill tracking
- Progress analytics

See [READING_MODULE.md](./READING_MODULE.md) for detailed documentation.

### ✅ Writing Coach
- 8 essay prompts across difficulties
- AI-powered scoring with Gemini API (with mock fallback)
- IELTS/TOEFL rubric-based feedback (4 criteria)
- Revision system with improvement tracking
- Detailed suggestions and outline recommendations

See [WRITING_MODULE.md](./WRITING_MODULE.md) for detailed documentation.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout user

### Reading Practice
- `GET /api/reading/next` - Get next adaptive reading item
- `GET /api/reading/items` - List all reading items
- `GET /api/reading/items/{id}` - Get specific reading item
- `POST /api/reading/submit` - Submit answer and get feedback
- `GET /api/reading/stats` - Get user reading statistics

### Writing Coach
- `GET /api/writing/prompts` - List essay prompts
- `GET /api/writing/prompts/{id}` - Get specific prompt
- `POST /api/writing/submit` - Submit essay for AI feedback
- `GET /api/writing/essays` - List user essays
- `GET /api/writing/essays/{id}` - Get specific essay with feedback
- `GET /api/writing/essays/{id}/revisions` - Get essay revisions
- `GET /api/writing/stats` - Get user writing statistics

### Future Endpoints
- Quest management endpoints
- Badge minting and retrieval endpoints
- Advanced analytics endpoints

## Color Palette

The application uses Claude's orange color palette:

- **Primary**: #FF7F4D
- **Primary Dark**: #E6652A
- **Primary Light**: #FFD4B8
- **Full palette**: claude-50 through claude-900

## Development

### Running Both Servers

Terminal 1 (Backend):
```bash
cd server
source venv/bin/activate
python main.py
```

Terminal 2 (Frontend):
```bash
cd client
npm run dev
```

### Building for Production

Frontend:
```bash
cd client
npm run build
```

Backend is production-ready with uvicorn.

## Next Steps

1. Implement reading practice module with adaptive difficulty
2. Integrate Gemini AI for essay scoring and feedback
3. Build quest system with rewards
4. Implement Web3 badge minting (Thirdweb + Polygon)
5. Add detailed analytics and progress tracking
6. Implement boss challenges and timed tests

## License

MIT
