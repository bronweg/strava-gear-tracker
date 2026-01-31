import requests
from datetime import datetime
from flask import current_app, url_for
from models import db, User, StravaToken


class StravaAuth:
    """Handle Strava OAuth 2.0 authentication."""
    
    @staticmethod
    def get_authorization_url():
        """Generate Strava authorization URL."""
        params = {
            'client_id': current_app.config['STRAVA_CLIENT_ID'],
            'redirect_uri': current_app.config['STRAVA_REDIRECT_URI'],
            'response_type': 'code',
            'scope': 'read,activity:read_all',
            'approval_prompt': 'auto'
        }
        
        url = current_app.config['STRAVA_AUTHORIZE_URL']
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{url}?{query_string}'
    
    @staticmethod
    def exchange_code_for_token(code):
        """Exchange authorization code for access token."""
        data = {
            'client_id': current_app.config['STRAVA_CLIENT_ID'],
            'client_secret': current_app.config['STRAVA_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(current_app.config['STRAVA_TOKEN_URL'], data=data)
        
        if response.status_code != 200:
            raise Exception(f'Failed to exchange code for token: {response.text}')
        
        return response.json()
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Refresh an expired access token."""
        data = {
            'client_id': current_app.config['STRAVA_CLIENT_ID'],
            'client_secret': current_app.config['STRAVA_CLIENT_SECRET'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(current_app.config['STRAVA_TOKEN_URL'], data=data)
        
        if response.status_code != 200:
            raise Exception(f'Failed to refresh token: {response.text}')
        
        return response.json()
    
    @staticmethod
    def save_user_and_token(token_data):
        """Save or update user and token information."""
        athlete = token_data['athlete']
        strava_id = athlete['id']
        
        # Find or create user
        user = User.query.filter_by(strava_id=strava_id).first()
        
        if not user:
            user = User(
                strava_id=strava_id,
                username=athlete.get('username'),
                firstname=athlete.get('firstname'),
                lastname=athlete.get('lastname'),
                profile_picture=athlete.get('profile')
            )
            db.session.add(user)
            db.session.flush()  # Get user.id
        else:
            # Update user info
            user.username = athlete.get('username')
            user.firstname = athlete.get('firstname')
            user.lastname = athlete.get('lastname')
            user.profile_picture = athlete.get('profile')
        
        # Save or update token
        strava_token = StravaToken.query.filter_by(user_id=user.id).first()
        
        if not strava_token:
            strava_token = StravaToken(
                user_id=user.id,
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                expires_at=token_data['expires_at']
            )
            db.session.add(strava_token)
        else:
            strava_token.access_token = token_data['access_token']
            strava_token.refresh_token = token_data['refresh_token']
            strava_token.expires_at = token_data['expires_at']
            strava_token.updated_at = datetime.utcnow()
        
        db.session.commit()
        return user
    
    @staticmethod
    def get_valid_token(user):
        """Get a valid access token for the user, refreshing if necessary."""
        strava_token = user.strava_token
        
        if not strava_token:
            raise Exception('No Strava token found for user')
        
        # Check if token is expired
        if strava_token.is_expired():
            # Refresh the token
            token_data = StravaAuth.refresh_access_token(strava_token.refresh_token)
            
            # Update token in database
            strava_token.access_token = token_data['access_token']
            strava_token.refresh_token = token_data['refresh_token']
            strava_token.expires_at = token_data['expires_at']
            strava_token.updated_at = datetime.utcnow()
            db.session.commit()
        
        return strava_token.access_token

