#!/bin/bash

# NVFlare Provisioning Dashboard - Complete Startup Script
# This script starts both the backend API and frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8443
FRONTEND_PORT=3000
BACKEND_DIR="$(dirname "$0")"
FRONTEND_DIR="$BACKEND_DIR/frontend"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}NVFlare Provisioning Dashboard${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing process on port $port (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Check Python environment
echo -e "${BLUE}Checking Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not detected${NC}"
    echo -e "${YELLOW}Make sure to activate your virtual environment first${NC}"
    echo -e "${YELLOW}Example: source ~/FL/bin/activate${NC}"
    echo ""
fi

# Check Node.js environment
echo -e "${BLUE}Checking Node.js environment...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo -e "${YELLOW}Please install Node.js 16+ and try again${NC}"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 14 ]; then
    echo -e "${YELLOW}Warning: Node.js version $(node --version) detected${NC}"
    echo -e "${YELLOW}This may cause compatibility issues. Recommended: Node.js 16+${NC}"
    echo ""
fi

# Check if ports are available
echo -e "${BLUE}Checking port availability...${NC}"
if check_port $BACKEND_PORT; then
    echo -e "${YELLOW}Port $BACKEND_PORT is already in use${NC}"
    read -p "Kill process on port $BACKEND_PORT? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port $BACKEND_PORT
    else
        echo -e "${RED}Cannot start backend. Port $BACKEND_PORT is in use.${NC}"
        exit 1
    fi
fi

if check_port $FRONTEND_PORT; then
    echo -e "${YELLOW}Port $FRONTEND_PORT is already in use${NC}"
    read -p "Kill process on port $FRONTEND_PORT? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port $FRONTEND_PORT
    else
        echo -e "${RED}Cannot start frontend. Port $FRONTEND_PORT is in use.${NC}"
        exit 1
    fi
fi

# Install backend dependencies if needed
echo -e "${BLUE}Checking backend dependencies...${NC}"
cd "$BACKEND_DIR"
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: requirements.txt not found in backend directory${NC}"
    exit 1
fi

# Install frontend dependencies if needed
echo -e "${BLUE}Checking frontend dependencies...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start backend
echo -e "${BLUE}Starting backend API...${NC}"
cd "$BACKEND_DIR"
echo -e "${GREEN}Backend will be available at: http://localhost:$BACKEND_PORT${NC}"
echo -e "${GREEN}API endpoints: http://localhost:$BACKEND_PORT/api/v1${NC}"
echo ""

# Start backend in background
python3 run_dashboard.py --host 0.0.0.0 --port $BACKEND_PORT --debug &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${BLUE}Waiting for backend to start...${NC}"
sleep 5

# Check if backend is running
if check_port $BACKEND_PORT; then
    echo -e "${GREEN}✓ Backend started successfully${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend
echo -e "${BLUE}Starting frontend...${NC}"
cd "$FRONTEND_DIR"
echo -e "${GREEN}Frontend will be available at: http://localhost:$FRONTEND_PORT${NC}"
echo ""

# Start frontend in background
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${BLUE}Waiting for frontend to start...${NC}"
sleep 10

# Check if frontend is running
if check_port $FRONTEND_PORT; then
    echo -e "${GREEN}✓ Frontend started successfully${NC}"
else
    echo -e "${RED}✗ Frontend failed to start${NC}"
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Dashboard started successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "${GREEN}Frontend:${NC} http://localhost:$FRONTEND_PORT"
echo -e "${GREEN}Backend API:${NC} http://localhost:$BACKEND_PORT"
echo -e "${GREEN}Backend Dashboard:${NC} http://localhost:$BACKEND_PORT"
echo ""
echo -e "${BLUE}Default Login:${NC}"
echo -e "${GREEN}Email:${NC} admin@example.com"
echo -e "${GREEN}Password:${NC} admin123"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}Stopping dashboard services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}Dashboard stopped${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running
wait

