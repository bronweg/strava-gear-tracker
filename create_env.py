#!/usr/bin/env python3
"""
Interactive script to create .env file with Strava credentials
"""

import secrets
import os


def create_env_file():
    """Create .env file interactively."""
    
    print("=" * 50)
    print("Bike Equipment Tracker - Environment Setup")
    print("=" * 50)
    print()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    print("Please provide your Strava API credentials.")
    print("If you don't have them yet, visit: https://www.strava.com/settings/api")
    print()
    
    # Get Strava credentials
    client_id = input("Strava Client ID: ").strip()
    client_secret = input("Strava Client Secret: ").strip()
    
    # Generate secret key
    secret_key = secrets.token_hex(32)
    
    # Default values
    redirect_uri = "http://localhost:5000/auth/callback"
    database_url = "sqlite:///bike_tracker.db"
    
    # Create .env content
    env_content = f"""# Flask Configuration
FLASK_SECRET_KEY={secret_key}

# Strava API Credentials
STRAVA_CLIENT_ID={client_id}
STRAVA_CLIENT_SECRET={client_secret}
STRAVA_REDIRECT_URI={redirect_uri}

# Database
DATABASE_URL={database_url}
"""
    
    # Write to file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print()
    print("✓ .env file created successfully!")
    print()
    print("Configuration:")
    print(f"  - Flask Secret Key: {secret_key[:20]}... (auto-generated)")
    print(f"  - Strava Client ID: {client_id}")
    print(f"  - Strava Client Secret: {'*' * len(client_secret)}")
    print(f"  - Redirect URI: {redirect_uri}")
    print(f"  - Database: {database_url}")
    print()
    print("You can now run the application with: python app.py")
    print()


if __name__ == '__main__':
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\nAborted.")
    except Exception as e:
        print(f"\nError: {e}")

