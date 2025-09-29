#!/bin/bash

# 🏦 AI Hedge Fund System - Unified Startup Script
# This script starts both the backend API and frontend development server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    local pids=$(lsof -t -i:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        print_warning "Killing existing processes on port $port"
        kill $pids 2>/dev/null || true
        sleep 2
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down system..."
    if [ ! -z "$API_PID" ]; then
        print_status "Stopping API server (PID: $API_PID)"
        kill $API_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        print_status "Stopping frontend server (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    print_success "System shutdown complete"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Print banner
echo -e "${BLUE}"
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│              🏦 AI Hedge Fund System v4.0.0                 │"
echo "│                                                             │"
echo "│  Professional-grade investment analysis with 4-agent       │"
echo "│  intelligence and narrative generation                      │"
echo "└─────────────────────────────────────────────────────────────┘"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "frontend" ] || [ ! -d "agents" ]; then
    print_error "Please run this script from the ai_hedge_fund_system root directory"
    exit 1
fi

print_status "Starting AI Hedge Fund System..."

# Check and install Python dependencies
print_status "Checking Python dependencies..."
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || {
    print_warning "Could not activate virtual environment, using system Python"
}

# Install/upgrade dependencies
pip install -r requirements.txt --quiet 2>/dev/null || {
    print_warning "Some Python dependencies might not be installed correctly"
}

# Check frontend dependencies
print_status "Checking frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi
cd ..

# Kill existing processes on our ports
kill_port 8010
kill_port 5174

print_status "Starting backend API server..."
# Start API server in background
python3 -m api.main &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Check if API started successfully
if check_port 8010; then
    print_success "API server started on http://localhost:8010"
else
    print_error "Failed to start API server on port 8010"
    exit 1
fi

# Test API health
print_status "Testing API health..."
if curl -s http://localhost:8010/health >/dev/null 2>&1; then
    print_success "API health check passed"
else
    print_warning "API health check failed, but server is running"
fi

print_status "Starting frontend development server..."
cd frontend
# Start frontend in background
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

if check_port 5174; then
    print_success "Frontend server started on http://localhost:5174"
elif check_port 5173; then
    print_success "Frontend server started on http://localhost:5173"
else
    print_warning "Frontend server may not have started correctly"
fi

# Display system information
echo -e "${GREEN}"
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│                   🚀 System Ready!                          │"
echo "│                                                             │"
echo "│  API Server:      http://localhost:8010                    │"
echo "│  API Docs:        http://localhost:8010/docs               │"
echo "│  Frontend:        http://localhost:5174                    │"
echo "│                                                             │"
echo "│  Press Ctrl+C to stop all services                         │"
echo "└─────────────────────────────────────────────────────────────┘"
echo -e "${NC}"

# Keep script running and monitor processes
print_status "Monitoring system status... (Press Ctrl+C to stop)"

while true; do
    # Check if processes are still running
    if ! kill -0 $API_PID 2>/dev/null; then
        print_error "API server stopped unexpectedly"
        break
    fi

    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend server stopped unexpectedly"
        break
    fi

    sleep 10
done

# Cleanup will be handled by the trap