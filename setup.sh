#!/bin/bash

# Setup script for AI Email Assistant
# This script sets up both backend and frontend

echo "==================================="
echo "AI Email Assistant - Setup Script"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Check Node version
echo "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Found Node.js $NODE_VERSION"
echo ""

# Setup Backend
echo "Setting up Backend..."
cd backend || exit

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo "Creating backend .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your credentials"
else
    echo "✅ Backend .env already exists"
fi

cd ..

# Setup Frontend
echo ""
echo "Setting up Frontend..."
cd frontend || exit

# Install dependencies
echo "Installing npm dependencies..."
npm install

# Create .env file
if [ ! -f .env ]; then
    echo "Creating frontend .env file..."
    cp .env.example .env
    echo "✅ Frontend .env created"
else
    echo "✅ Frontend .env already exists"
fi

cd ..

echo ""
echo "==================================="
echo "✅ Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your Google OAuth and OpenAI credentials"
echo "2. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "See QUICKSTART.md for detailed instructions!"
