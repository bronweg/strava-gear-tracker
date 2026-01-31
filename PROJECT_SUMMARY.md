# Strava Gear Tracker - Project Summary

## Overview

A complete Python web application for tracking bicycle gear and component wear with Strava integration. The application automatically calculates equipment statistics (distance, time, days) by fetching activities from Strava API.

## ✅ Completed Features

### Core Functionality
- ✅ **Equipment Management**: Full CRUD operations for bicycle equipment
- ✅ **Multi-Bike Support**: Automatic syncing of bikes from Strava
- ✅ **Bike-Specific Tracking**: Associate equipment with specific bikes for accurate wear tracking
- ✅ **Strava OAuth 2.0**: Secure authentication with Strava accounts
- ✅ **Activity Tracking**: Automatic fetching of Strava activities since installation date
- ✅ **Statistics Calculation**: Total distance (km), riding time (hours), days elapsed
- ✅ **Smart Filtering**: Bike-specific activity filtering and virtual ride exclusion
- ✅ **User-Friendly Interface**: Responsive web design with Bootstrap 5

### Technical Implementation
- ✅ **Flask Web Framework**: Clean MVC architecture
- ✅ **SQLAlchemy ORM**: Database models for User, Equipment, StravaToken, StravaBike
- ✅ **Flask-Login**: Session management and authentication
- ✅ **Strava API Integration**: Rate limiting, token refresh, pagination, bike syncing
- ✅ **SQLite Database**: Persistent data storage
- ✅ **Error Handling**: Comprehensive error handling for API failures
- ✅ **Backward Compatibility**: Existing equipment without bike associations still works

## 📁 Project Structure

```
strava-gear-tracker/
├── app.py                    # Main Flask application with routes
├── config.py                 # Configuration management
├── models.py                 # Database models (User, Equipment, StravaToken, StravaBike)
├── strava_auth.py           # Strava OAuth 2.0 handler
├── strava_service.py        # Strava API integration with bike support
├── equipment_service.py     # Equipment CRUD operations and bike management
├── create_env.py            # Interactive .env file creator
├── requirements.txt         # Python dependencies
├── setup.sh                 # Automated setup script (Unix)
├── setup.bat                # Automated setup script (Windows)
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # Main documentation
├── QUICKSTART.md           # Quick start guide
├── DEPLOYMENT.md           # Deployment guide
├── PROJECT_SUMMARY.md      # This file
└── templates/              # HTML templates
    ├── base.html           # Base template with navigation
    ├── login.html          # Login page with Strava OAuth
    ├── dashboard.html      # Equipment dashboard with statistics
    ├── add_equipment.html  # Add equipment form
    └── edit_equipment.html # Edit equipment form
```

## 🎨 User Interface Pages

1. **Login Page** (`/login`)
   - Strava OAuth connection button
   - Feature highlights
   - Clean, modern design

2. **Dashboard** (`/dashboard`)
   - Grid view of all equipment
   - Real-time statistics for each item
   - Quick actions (edit, delete)
   - Empty state for new users

3. **Add Equipment** (`/equipment/add`)
   - Form with name, type, installation date, notes
   - Predefined equipment types dropdown
   - Date picker with validation

4. **Edit Equipment** (`/equipment/edit/<id>`)
   - Pre-filled form with existing data
   - Update or delete options
   - Confirmation for destructive actions

## 🔧 Technical Architecture

### Database Models

**User**
- Strava user information
- One-to-many relationship with Equipment
- One-to-one relationship with StravaToken

**Equipment**
- Name, type, installation date, notes
- Belongs to a User
- Tracks creation and update timestamps

**StravaToken**
- OAuth access and refresh tokens
- Token expiration tracking
- Automatic token refresh

### Services Layer

**StravaAuth**
- OAuth authorization URL generation
- Code-to-token exchange
- Token refresh logic
- User and token persistence

**StravaService**
- Activity fetching with pagination
- Rate limit handling
- Statistics calculation
- Activity filtering (ride types only)

**EquipmentService**
- CRUD operations
- Equipment with statistics retrieval
- User-scoped queries

## 🚀 Quick Start

### Option 1: Automated Setup

```bash
./setup.sh  # On macOS/Linux
# or
setup.bat   # On Windows
```

### Option 2: Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_env.py
python app.py
```

## 📊 Statistics Tracked

For each equipment item:
- **Total Distance**: Kilometers ridden since installation
- **Total Time**: Hours of riding time
- **Days Elapsed**: Calendar days since installation
- **Ride Count**: Number of rides completed

## 🔐 Security Features

- OAuth 2.0 for secure authentication
- Session-based user management
- Secure token storage
- CSRF protection ready
- Environment-based configuration

## 🌐 API Integration

### Strava API Features Used
- OAuth 2.0 authentication
- Athlete endpoint (for fetching bikes/gear)
- Athlete activities endpoint
- Automatic token refresh
- Rate limit handling
- Pagination support
- Bike/gear syncing

### Multi-Bike Support
- **Bike Syncing**: Automatically fetches and stores bikes from Strava
- **Bike Association**: Equipment can be linked to specific bikes
- **Bike Filtering**: Activities filtered by gear_id when bike is specified
- **Backward Compatible**: Equipment without bike association counts all activities
- **Display**: Shows bike name/nickname in dashboard and forms

### Activity Types Tracked
- **Ride**: Outdoor bicycle rides
- **EBikeRide**: Electric bicycle rides

**Note**: VirtualRide activities (indoor/virtual rides on platforms like Zwift, TrainerRoad, etc.) are intentionally excluded from equipment statistics. Virtual rides don't cause wear on outdoor bicycle components like chains, tires, cassettes, and other equipment, so they shouldn't count toward equipment lifespan tracking.

**Bike Filtering**: When equipment is associated with a specific bike, only activities recorded with that bike (matching gear_id) are counted toward the equipment's statistics.

## 📝 Configuration

All configuration via environment variables:
- `FLASK_SECRET_KEY`: Session encryption
- `STRAVA_CLIENT_ID`: Strava API client ID
- `STRAVA_CLIENT_SECRET`: Strava API client secret
- `STRAVA_REDIRECT_URI`: OAuth callback URL
- `DATABASE_URL`: Database connection string

## 🎯 Next Steps for Users

1. **Get Strava API Credentials**
   - Visit https://www.strava.com/settings/api
   - Create an application
   - Note Client ID and Client Secret

2. **Run Setup**
   - Use automated setup script or manual installation
   - Configure environment variables

3. **Start Application**
   - Run `python app.py`
   - Open http://localhost:5000

4. **Add Equipment**
   - Login with Strava
   - Add your bicycle equipment
   - View automatic statistics

## 📚 Documentation Files

- **README.md**: Comprehensive documentation
- **QUICKSTART.md**: 5-minute setup guide
- **DEPLOYMENT.md**: Production deployment guide
- **PROJECT_SUMMARY.md**: This overview

## 🛠️ Technologies Used

- **Backend**: Python 3.8+, Flask 3.0
- **Database**: SQLAlchemy, SQLite
- **Authentication**: Flask-Login, OAuth 2.0
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **API**: Strava API v3
- **HTTP Client**: Requests library

## ✨ Highlights

- **Zero Configuration**: Automated setup scripts
- **Production Ready**: Deployment guide included
- **Well Documented**: Multiple documentation files
- **Clean Code**: Modular architecture with services
- **Error Handling**: Graceful degradation on API failures
- **Responsive Design**: Works on desktop and mobile
- **User Experience**: Intuitive interface with visual feedback

## 📦 Deliverables

All requirements met:
✅ Equipment management (CRUD)
✅ Strava OAuth integration
✅ Activity fetching and statistics
✅ Web interface with multiple pages
✅ Persistent storage
✅ Rate limit handling
✅ Secure token storage
✅ Error handling
✅ Complete documentation
✅ Setup automation

