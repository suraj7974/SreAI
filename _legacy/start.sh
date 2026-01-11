#!/bin/bash
# Quick start script for AI Chaos Handler

set -e

echo "🚀 AI Chaos Handler - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }
echo "✅ Python OK"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env - Please edit it with your configuration"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo "✅ Dependencies installed"

# Build frontend
echo ""
echo "Building frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install > /dev/null 2>&1
fi
npm run build:css > /dev/null 2>&1
cd ..
echo "✅ Frontend built"

# Create incidents directory
echo ""
echo "Creating incidents directory..."
mkdir -p incidents
echo "✅ Directory created"

# Start the application
echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Starting AI Chaos Handler..."
echo "Dashboard will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo "=================================="
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
