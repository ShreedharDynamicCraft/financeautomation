#!/bin/bash

# Development setup script for PDF Extraction Project

echo "🚀 Setting up PDF Extraction Project for Development"
echo "=================================================="

# Check if required tools are installed
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

echo "📋 Checking prerequisites..."
check_command "node"
check_command "npm"
check_command "python3"
check_command "pip3"

# Setup backend
echo ""
echo "🐍 Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit backend/.env and add your GOOGLE_API_KEY"
fi

# Create necessary directories
mkdir -p uploads outputs logs

cd ..

# Setup frontend
echo ""
echo "⚛️  Setting up Frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

# Create run script
echo ""
echo "📝 Creating run scripts..."

cat > scripts/start-dev.sh << 'EOF'
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
EOF

chmod +x scripts/start-dev.sh

# Create stop script
cat > scripts/stop-dev.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping PDF Extraction Project"
echo "=================================="

# Kill processes
pkill -f "uvicorn.*app.main"
pkill -f "npm start"

echo "✅ All services stopped"
EOF

chmod +x scripts/stop-dev.sh

echo ""
echo "🎉 Setup Complete!"
echo "================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit backend/.env and add your GOOGLE_API_KEY"
echo "2. Run: ./scripts/start-dev.sh (for development)"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "⚠️  Important: Make sure to get your Google AI Studio API key!"
echo "   Visit: https://aistudio.google.com/app/apikey"