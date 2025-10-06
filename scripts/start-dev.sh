#!/bin/bash

echo "🚀 Starting PDF Extraction Project in Development Mode"
echo "====================================================="

# Function to run command in new terminal tab (macOS)
run_in_tab() {
    osascript -e "tell app \"Terminal\" to do script \"cd $(pwd) && $1\""
}

# Start services in separate tabs
echo "Starting services..."
run_in_tab "cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
sleep 2
run_in_tab "cd frontend && npm start"

echo ""
echo "✅ All services are starting!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To stop all services, close the terminal tabs or use Ctrl+C in each"
