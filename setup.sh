#!/bin/bash

# Bike Equipment Tracker Setup Script

echo "=========================================="
echo "Bike Equipment Tracker - Setup Script"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Update the .env file with the generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-this/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-change-this/$SECRET_KEY/" .env
    fi
    
    echo "✓ .env file created with random secret key"
    echo ""
    echo "⚠️  IMPORTANT: You need to add your Strava API credentials to the .env file"
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://www.strava.com/settings/api"
    echo "2. Create a new application"
    echo "3. Copy your Client ID and Client Secret"
    echo "4. Edit the .env file and replace:"
    echo "   - STRAVA_CLIENT_ID=your-strava-client-id"
    echo "   - STRAVA_CLIENT_SECRET=your-strava-client-secret"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "1. Make sure your Strava credentials are in the .env file"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the application: python app.py"
echo "4. Open your browser to: http://localhost:5000"
echo ""

