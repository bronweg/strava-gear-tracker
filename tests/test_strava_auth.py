"""
Unit tests for Strava authentication.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from strava_auth import StravaAuth
from models import db, User, StravaToken


class TestStravaAuth:
    """Tests for the StravaAuth class."""
    
    def test_get_authorization_url(self, app):
        """Test generating Strava authorization URL."""
        with app.app_context():
            url = StravaAuth.get_authorization_url()
            
            assert 'https://www.strava.com/oauth/authorize' in url
            assert 'client_id=test_client_id' in url
            assert 'redirect_uri=http://localhost:5000/auth/callback' in url
            assert 'response_type=code' in url
            assert 'scope=read,activity:read_all' in url
            assert 'approval_prompt=auto' in url
    
    @patch('strava_auth.requests.post')
    def test_exchange_code_for_token_success(self, mock_post, app, mock_strava_token_response):
        """Test successful code-to-token exchange."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_strava_token_response
        mock_post.return_value = mock_response
        
        with app.app_context():
            result = StravaAuth.exchange_code_for_token('test_code')
            
            assert result == mock_strava_token_response
            mock_post.assert_called_once()
            
            # Verify the request data
            call_args = mock_post.call_args
            assert call_args[1]['data']['client_id'] == 'test_client_id'
            assert call_args[1]['data']['client_secret'] == 'test_client_secret'
            assert call_args[1]['data']['code'] == 'test_code'
            assert call_args[1]['data']['grant_type'] == 'authorization_code'
    
    @patch('strava_auth.requests.post')
    def test_exchange_code_for_token_failure(self, mock_post, app):
        """Test failed code-to-token exchange."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        with app.app_context():
            with pytest.raises(Exception) as exc_info:
                StravaAuth.exchange_code_for_token('invalid_code')
            
            assert 'Failed to exchange code for token' in str(exc_info.value)
    
    @patch('strava_auth.requests.post')
    def test_refresh_access_token_success(self, mock_post, app):
        """Test successful token refresh."""
        mock_response_data = {
            'token_type': 'Bearer',
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_at': int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
            'expires_in': 21600
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response
        
        with app.app_context():
            result = StravaAuth.refresh_access_token('old_refresh_token')
            
            assert result == mock_response_data
            assert result['access_token'] == 'new_access_token'
            
            # Verify the request data
            call_args = mock_post.call_args
            assert call_args[1]['data']['refresh_token'] == 'old_refresh_token'
            assert call_args[1]['data']['grant_type'] == 'refresh_token'
    
    @patch('strava_auth.requests.post')
    def test_refresh_access_token_failure(self, mock_post, app):
        """Test failed token refresh."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        with app.app_context():
            with pytest.raises(Exception) as exc_info:
                StravaAuth.refresh_access_token('invalid_refresh_token')
            
            assert 'Failed to refresh token' in str(exc_info.value)
    
    def test_save_user_and_token_new_user(self, app, mock_strava_token_response):
        """Test saving a new user and token."""
        with app.app_context():
            user = StravaAuth.save_user_and_token(mock_strava_token_response)
            
            assert user is not None
            assert user.strava_id == 12345
            assert user.username == 'testuser'
            assert user.firstname == 'Test'
            assert user.lastname == 'User'
            assert user.profile_picture == 'http://example.com/profile.jpg'
            
            # Verify token was saved
            token = StravaToken.query.filter_by(user_id=user.id).first()
            assert token is not None
            assert token.access_token == 'mock_access_token'
            assert token.refresh_token == 'mock_refresh_token'
    
    def test_save_user_and_token_existing_user(self, app, test_user, mock_strava_token_response):
        """Test updating an existing user and token."""
        with app.app_context():
            # Modify the mock response to match the existing user
            mock_strava_token_response['athlete']['id'] = test_user.strava_id
            mock_strava_token_response['athlete']['username'] = 'updated_username'
            
            user = StravaAuth.save_user_and_token(mock_strava_token_response)
            
            assert user.id == test_user.id
            assert user.username == 'updated_username'
            
            # Verify token was saved
            token = StravaToken.query.filter_by(user_id=user.id).first()
            assert token is not None
            assert token.access_token == 'mock_access_token'
    
    def test_save_user_and_token_update_existing_token(self, app, test_user_with_token, mock_strava_token_response):
        """Test updating an existing user's token."""
        with app.app_context():
            # Get the existing token
            old_token = test_user_with_token.strava_token
            old_access_token = old_token.access_token
            
            # Modify the mock response to match the existing user
            mock_strava_token_response['athlete']['id'] = test_user_with_token.strava_id
            
            user = StravaAuth.save_user_and_token(mock_strava_token_response)
            
            # Verify the token was updated, not created new
            token = StravaToken.query.filter_by(user_id=user.id).first()
            assert token.id == old_token.id
            assert token.access_token == 'mock_access_token'
            assert token.access_token != old_access_token
    
    def test_get_valid_token_not_expired(self, app, test_user_with_token):
        """Test getting a valid token that hasn't expired."""
        with app.app_context():
            token = StravaAuth.get_valid_token(test_user_with_token)
            
            assert token == 'test_access_token'
    
    @patch('strava_auth.StravaAuth.refresh_access_token')
    def test_get_valid_token_expired(self, mock_refresh, app, test_user):
        """Test getting a valid token when the current one is expired."""
        with app.app_context():
            # Create an expired token
            expires_at = int((datetime.utcnow() - timedelta(hours=1)).timestamp())
            token = StravaToken(
                user_id=test_user.id,
                access_token='old_access_token',
                refresh_token='old_refresh_token',
                expires_at=expires_at
            )
            db.session.add(token)
            db.session.commit()

            # Mock the refresh response
            mock_refresh.return_value = {
                'access_token': 'new_access_token',
                'refresh_token': 'new_refresh_token',
                'expires_at': int((datetime.utcnow() + timedelta(hours=6)).timestamp())
            }

            # Get the valid token (should trigger refresh)
            valid_token = StravaAuth.get_valid_token(test_user)

            # Verify the refresh was called and new token was returned
            assert valid_token == 'new_access_token'
            mock_refresh.assert_called_once_with('old_refresh_token')

    def test_get_valid_token_no_token(self, app, test_user):
        """Test getting a valid token when user has no token."""
        with app.app_context():
            with pytest.raises(Exception) as exc_info:
                StravaAuth.get_valid_token(test_user)

            assert 'No Strava token found for user' in str(exc_info.value)


