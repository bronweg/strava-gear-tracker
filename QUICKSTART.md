# Quick Start Guide

Get your Bike Equipment Tracker up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher installed
- A Strava account
- Internet connection

## Step 1: Get Strava API Credentials

1. Go to https://www.strava.com/settings/api
2. If you don't have an application, create one:
   - **Application Name**: Bike Equipment Tracker
   - **Category**: Training
   - **Club**: Leave blank
   - **Website**: http://localhost:5000
   - **Application Description**: Track bicycle equipment usage
   - **Authorization Callback Domain**: localhost
3. Click "Create"
4. Note your **Client ID** and **Client Secret**

## Step 2: Automated Setup (Recommended)

### On macOS/Linux:

```bash
./setup.sh
```

### On Windows:

```cmd
setup.bat
```

The setup script will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file with a random secret key

## Step 3: Configure Strava Credentials

Edit the `.env` file and add your Strava credentials:

```bash
STRAVA_CLIENT_ID=12345  # Replace with your Client ID
STRAVA_CLIENT_SECRET=abcdef123456  # Replace with your Client Secret
```

## Step 4: Run the Application

### On macOS/Linux:

```bash
source venv/bin/activate
python app.py
```

### On Windows:

```cmd
venv\Scripts\activate.bat
python app.py
```

## Step 5: Access the Application

Open your browser and go to: http://localhost:5000

## Step 6: Login with Strava

1. Click "Connect with Strava"
2. Authorize the application
3. You'll be redirected to your dashboard

## Step 7: Add Your First Equipment

1. Click "Add Equipment"
2. Fill in the details:
   - Name: e.g., "Chain"
   - Type: Select "Chain"
   - Installation Date: When you installed it
   - Notes: Optional
3. Click "Add Equipment"

The app will automatically fetch your outdoor Strava rides and calculate equipment statistics!

**Note**: Only outdoor rides (Ride) and e-bike rides (EBikeRide) are counted. Virtual/indoor rides are excluded since they don't cause wear on outdoor bicycle components.

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use any text editor

# Run the application
python app.py
```

## Troubleshooting

### "Module not found" errors

Make sure you've activated the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
```

### "Failed to exchange code for token"

Double-check your Strava Client ID and Client Secret in the `.env` file.

### "Authorization Callback Domain" error

Make sure you set the callback domain to `localhost` in your Strava API settings.

### Port 5000 already in use

You can change the port by editing `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to any available port
```

## Next Steps

- Add all your bicycle equipment
- View statistics on the dashboard
- Edit or delete equipment as needed
- Monitor your equipment lifespan

## Need Help?

Check the full [README.md](README.md) for detailed documentation.

