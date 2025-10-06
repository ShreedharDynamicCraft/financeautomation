#!/bin/bash

echo "🛑 Stopping PDF Extraction Project"
echo "=================================="

# Kill processes
pkill -f "uvicorn.*app.main"
pkill -f "npm start"

echo "✅ All services stopped"
