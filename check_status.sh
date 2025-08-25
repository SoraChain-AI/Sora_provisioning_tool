#!/bin/bash

# NVFlare Provisioning Dashboard - Status Check Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8443
FRONTEND_PORT=3000

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Sorachain Dashboard Status Check${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to check port status
check_port() {
    local port=$1
    local service=$2
    local url=$3
    
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        local pid=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
        local process=$(ps -p $pid -o comm= 2>/dev/null || echo "Unknown")
        echo -e "${GREEN}✓ $service is running${NC}"
        echo -e "  Port: $port"
        echo -e "  PID: $pid"
        echo -e "  Process: $process"
        echo -e "  URL: $url"
        
        # Test if service is responding
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "  ${GREEN}Status: Responding${NC}"
        else
            echo -e "  ${YELLOW}Status: Port open but not responding${NC}"
        fi
    else
        echo -e "${RED}✗ $service is not running${NC}"
        echo -e "  Port: $port (not in use)"
    fi
    echo ""
}

# Check backend status
echo -e "${BLUE}Backend API Status:${NC}"
check_port $BACKEND_PORT "Backend API" "http://localhost:$BACKEND_PORT"

# Check frontend status
echo -e "${BLUE}Frontend Status:${NC}"
check_port $FRONTEND_PORT "Frontend" "http://localhost:$FRONTEND_PORT"

# Check database
echo -e "${BLUE}Database Status:${NC}"
if [ -f "provisioning_dashboard.db" ]; then
    echo -e "${GREEN}✓ Database file exists${NC}"
    echo -e "  File: provisioning_dashboard.db"
    echo -e "  Size: $(du -h provisioning_dashboard.db | cut -f1)"
else
    echo -e "${RED}✗ Database file not found${NC}"
fi
echo ""

# Check NVFlare installation
echo -e "${BLUE}NVFlare Installation:${NC}"
if command -v nvflare &> /dev/null; then
    echo -e "${GREEN}✓ NVFlare CLI is installed${NC}"
    echo -e "  Version: $(nvflare --version 2>/dev/null || echo 'Unknown')"
else
    echo -e "${RED}✗ NVFlare CLI is not installed${NC}"
    echo -e "  Please install NVFlare to use provisioning features"
fi
echo ""

# Check Python environment
echo -e "${BLUE}Python Environment:${NC}"
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✓ Virtual environment is activated${NC}"
    echo -e "  Path: $VIRTUAL_ENV"
    echo -e "  Python: $(python3 --version)"
else
    echo -e "${YELLOW}⚠ Virtual environment not detected${NC}"
    echo -e "  Current Python: $(python3 --version)"
fi
echo ""

# Check Node.js environment
echo -e "${BLUE}Node.js Environment:${NC}"
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js is installed${NC}"
    echo -e "  Version: $(node --version)"
    echo -e "  NPM: $(npm --version)"
else
    echo -e "${RED}✗ Node.js is not installed${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}================================${NC}"

backend_running=$(netstat -tlnp 2>/dev/null | grep -q ":$BACKEND_PORT " && echo "Yes" || echo "No")
frontend_running=$(netstat -tlnp 2>/dev/null | grep -q ":$FRONTEND_PORT " && echo "Yes" || echo "No")

echo -e "Backend API: $backend_running"
echo -e "Frontend: $frontend_running"

if [ "$backend_running" = "Yes" ] && [ "$frontend_running" = "Yes" ]; then
    echo ""
    echo -e "${GREEN}🎉 Dashboard is fully operational!${NC}"
    echo -e "${GREEN}Access your dashboard at: http://localhost:$FRONTEND_PORT${NC}"
elif [ "$backend_running" = "Yes" ]; then
    echo ""
    echo -e "${YELLOW}⚠ Backend is running but frontend is not${NC}"
    echo -e "${YELLOW}Start frontend with: ./start_frontend.sh${NC}"
elif [ "$frontend_running" = "Yes" ]; then
    echo ""
    echo -e "${YELLOW}⚠ Frontend is running but backend is not${NC}"
    echo -e "${YELLOW}Start backend with: python3 run_dashboard.py --host 0.0.0.0 --port $BACKEND_PORT --debug${NC}"
else
    echo ""
    echo -e "${RED}❌ Dashboard is not running${NC}"
    echo -e "${RED}Start complete dashboard with: ./start_dashboard.sh${NC}"
fi




