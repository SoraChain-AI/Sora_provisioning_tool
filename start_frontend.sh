#!/bin/bash

# NVFlare Provisioning Dashboard Frontend Startup Script

echo "Starting NVFlare Provisioning Dashboard Frontend..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ and try again"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 14 ]; then
    echo "Warning: Node.js version $(node --version) detected"
    echo "This may cause compatibility issues. Recommended: Node.js 16+"
    echo "Continuing anyway..."
fi

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || {
    echo "Error: Could not navigate to frontend directory"
    exit 1
}

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check if backend is running
echo "Checking backend status..."
if curl -s http://localhost:8443/api/v1/users > /dev/null 2>&1; then
    echo "✓ Backend is running on port 8443"
else
    echo "⚠ Warning: Backend is not accessible on port 8443"
    echo "Make sure the backend is running before using the frontend"
fi

# Start the frontend
echo "Starting frontend development server..."
echo "Frontend will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo ""

npm start
