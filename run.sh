#!/bin/bash

# Exit on error
set -e

echo "=== AI Interview Platform Setup and Startup Script ==="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory structure if it doesn't exist
echo "Creating upload directories..."
mkdir -p uploads/cvs uploads/profile_pics uploads/audio

# Create default profile image if it doesn't exist
echo "Ensuring default profile image exists..."
mkdir -p app/static/img
if [ ! -f "app/static/img/default.jpg" ]; then
    echo "Creating default profile image..."
    echo "Default profile image" > app/static/img/default.jpg
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
GOOGLE_API_KEY=AIzaSyA7zgkfPqewfQsGhQi7L8OYVxsiZuOguSU
SECRET_KEY=2a8a74a1c4e9d2b7f5e8c6a3d7b9f1e0
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db
EOF
    echo ".env file created with your API key."
fi

# Handle database setup
echo "Setting up database..."
if [ ! -d "migrations" ]; then
    echo "Initializing Flask-Migrate..."
    flask db init
fi

# Apply migrations
echo "Applying migrations..."
if [ ! -f "app.db" ]; then
    # If no database exists, create initial migration
    echo "Creating initial migration..."
    flask db migrate -m "Initial migration"
    flask db upgrade
    
    # Seed database with questions
    echo "Seeding database with questions..."
    python seed_db.py
else
    # Database already exists, check if there are new migrations to apply
    echo "Checking for pending migrations..."
    flask db upgrade
fi

# Start directly with Python instead of using flask run
echo "Starting AI Interview Platform on port 5008..."
echo "You can test if the server is running by visiting:"
echo "http://localhost:5008/test (JSON response)"
echo "http://localhost:5008/test-page (Simple HTML page)"
echo ""
echo "NOTE: If you see a template error, try one of the test URLs above first"
echo ""

# Run with Python directly
python run.py

# Note: The script never reaches this point when flask is running,
# these instructions are shown if the user stops the server with Ctrl+C
echo "Server stopped. To restart, run: ./run.sh"
echo "Access the application at http://localhost:5008 or http://[your-ip]:5008"