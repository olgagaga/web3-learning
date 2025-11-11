#!/bin/bash

echo "=================================="
echo "Web3 Education Platform Setup"
echo "=================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.10+ first."
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL 14+ first."
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Setup backend
echo "Setting up backend..."
cd server

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your database credentials and API keys"
fi

cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd client

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

cd ..

# Database setup reminder
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Create PostgreSQL database: sudo -u postgres psql -c 'CREATE DATABASE web3_edu_platform;'"
echo "2. Run database schema: sudo -u postgres psql -d web3_edu_platform -f server/database/schema.sql"
echo "3. Update server/.env with your database credentials and Gemini API key"
echo "4. Start backend: cd server && source venv/bin/activate && python main.py"
echo "5. Start frontend (in new terminal): cd client && npm run dev"
echo ""
echo "Then visit http://localhost:3000"
