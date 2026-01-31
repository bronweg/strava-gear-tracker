# Strava Gear Tracker

A Python web application for tracking bicycle gear and component wear with Strava integration. Monitor your equipment's lifespan by automatically calculating total distance, riding time, and days since installation using your Strava activities.

## Features

- **Strava OAuth Integration**: Secure login with your Strava account
- **Multi-Bike Support**: Automatically sync your bikes from Strava and track equipment per bike
- **Equipment Management**: Add, edit, and delete bicycle equipment items
- **Bike-Specific Tracking**: Associate equipment with specific bikes for accurate wear tracking
- **Automatic Statistics**: Calculate total distance (km), riding time (hours), and days since installation
- **Activity Tracking**: Fetch outdoor rides (Ride) and e-bike rides (EBikeRide) from equipment installation date to present
- **Smart Filtering**: Virtual/indoor rides are excluded from equipment wear calculations since they don't affect outdoor components
- **User-Friendly Interface**: Clean, responsive web interface with Bootstrap 5
- **Persistent Storage**: SQLite database for storing equipment and user data

## Screenshots

### Dashboard
View all your equipment with real-time statistics from Strava.

### Equipment Management
Easily add, edit, or delete equipment items with installation dates.

## Requirements

- Python 3.8 or higher
- Strava account
- Strava API credentials (Client ID and Client Secret)

## Installation

### 1. Clone or Download the Repository

```bash
cd /path/to/your/project
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Strava API Credentials

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create a new application:
   - **Application Name**: Strava Gear Tracker (or your choice)
   - **Category**: Training
   - **Website**: http://localhost:5000
   - **Authorization Callback Domain**: localhost
3. Note your **Client ID** and **Client Secret**

### 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Strava credentials:

```
FLASK_SECRET_KEY=your-random-secret-key-here
STRAVA_CLIENT_ID=your-strava-client-id
STRAVA_CLIENT_SECRET=your-strava-client-secret
STRAVA_REDIRECT_URI=http://localhost:5000/auth/callback
DATABASE_URL=sqlite:///bike_tracker.db
```

**Important**: Generate a secure secret key for Flask:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at: http://localhost:5000

## Usage

### First Time Setup

1. Navigate to http://localhost:5000
2. Click "Connect with Strava"
3. Authorize the application on Strava
4. You'll be redirected back to the dashboard

### Adding Equipment

1. Click "Add Equipment" in the navigation or dashboard
2. Fill in the equipment details:
   - **Name**: e.g., "Front Tire", "Chain"
   - **Type**: Select from predefined types or leave blank
   - **Installation Date**: When you installed the equipment
   - **Associated Bike**: Select a specific bike or "All bikes" for equipment used across multiple bikes
   - **Notes**: Optional additional information
3. Click "Add Equipment"

**Bike-Specific Tracking**: When you select a specific bike, only activities recorded with that bike will be counted toward the equipment's statistics. This is perfect for bike-specific components like chains, cassettes, or tires. For equipment used across multiple bikes (like pedals or a saddle), select "All bikes".

### Viewing Statistics

The dashboard automatically displays for each equipment item:
- **Total Distance**: Kilometers ridden since installation (outdoor rides only)
- **Total Time**: Hours ridden since installation (outdoor rides only)
- **Days Elapsed**: Calendar days since installation
- **Ride Count**: Number of outdoor rides since installation

**Note**: Statistics include only outdoor rides (Ride) and e-bike rides (EBikeRide). Virtual/indoor rides (VirtualRide) are excluded because they don't cause wear on outdoor bicycle components like chains, tires, and cassettes.

### Editing Equipment

1. Click the three-dot menu on any equipment card
2. Select "Edit"
3. Update the information
4. Click "Update Equipment"

### Deleting Equipment

1. Click the three-dot menu on any equipment card
2. Select "Delete"
3. Confirm the deletion

## Project Structure

```
strava-gear-tracker/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── strava_auth.py         # Strava OAuth handling
├── strava_service.py      # Strava API integration
├── equipment_service.py   # Equipment CRUD operations
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── templates/            # HTML templates
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── add_equipment.html
    └── edit_equipment.html
```

## Technical Details

### Database Schema

- **Users**: Strava user information
- **Equipment**: Equipment items with installation dates and optional bike associations
- **StravaToken**: OAuth tokens for API access
- **StravaBike**: Synced bikes/gear from Strava with names, brands, and models

### Multi-Bike Support

The application automatically syncs your bikes from Strava:
- Bikes are fetched from the Strava API when you log in or visit the dashboard
- Each bike's name, nickname, brand, and model are stored locally
- Equipment can be associated with a specific bike or marked as "All bikes"
- When equipment is bike-specific, only activities recorded with that bike are counted
- Backward compatible: existing equipment without bike associations counts all activities

### Activity Filtering

The application intelligently filters Strava activities for equipment tracking:
- **Included**: Outdoor rides (Ride) and e-bike rides (EBikeRide)
- **Excluded**: Virtual/indoor rides (VirtualRide)
- **Bike Filtering**: When equipment is associated with a specific bike, only activities with that bike's gear_id are counted
- **Rationale**: Virtual rides don't cause wear on outdoor bicycle components, so they shouldn't count toward equipment lifespan

### API Rate Limiting

The application handles Strava API rate limits automatically:
- Implements retry logic with exponential backoff
- Adds delays between paginated requests
- Refreshes expired access tokens automatically

### Security

- OAuth 2.0 for secure authentication
- Session-based user management with Flask-Login
- Secure token storage in database
- CSRF protection on forms

## Troubleshooting

### "No Strava token found for user"

Make sure you've completed the OAuth flow by logging in with Strava.

### "Failed to exchange code for token"

Check that your Strava Client ID and Client Secret are correct in the `.env` file.

### "Rate limit exceeded"

The app handles this automatically, but if you're making many requests, wait a few minutes.

## License

This project is open source and available for personal use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Support

For issues or questions, please create an issue in the repository.

