#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Change to project root (parent of scripts/)
cd "$SCRIPT_DIR/.."

echo "===================================="
echo "Multi-Agent Code Generator - Web UI"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env file with your configuration."
    echo "See .env.example for reference."
    echo ""
    read -p "Press Enter to continue anyway..."
fi

# Install Python dependencies if needed
echo "Checking Python dependencies..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -r backend/requirements.txt
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "===================================="
echo "Starting servers..."
echo "===================================="
echo ""
echo "Backend API will run on: http://localhost:5000"
echo "Frontend UI will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
python3 -m backend.api_server &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "Servers are running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "The UI will open automatically in your browser."
echo "Press Ctrl+C to stop both servers."
echo ""

# Wait for processes
wait
