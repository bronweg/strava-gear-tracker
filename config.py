import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bike_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Strava OAuth
    STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
    STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
    STRAVA_REDIRECT_URI = os.getenv('STRAVA_REDIRECT_URI', 'http://localhost:5000/auth/callback')
    
    # Strava API
    STRAVA_AUTHORIZE_URL = 'https://www.strava.com/oauth/authorize'
    STRAVA_TOKEN_URL = 'https://www.strava.com/oauth/token'
    STRAVA_API_BASE_URL = 'https://www.strava.com/api/v3'

