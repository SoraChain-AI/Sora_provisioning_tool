#!/bin/bash

# Restart Frontend with Fixed ESLint Configuration

echo "Restarting frontend with fixed ESLint configuration..."

# Kill existing frontend process
pkill -f "npm start" || true
pkill -f "react-scripts start" || true

# Wait a moment
sleep 2

# Clear any cached files
cd frontend
rm -rf node_modules/.cache
rm -rf build

# Start frontend again
echo "Starting frontend..."
npm start




