"""
Integration tests for Flask application routes.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from flask_login import login_user
from models import db, Equipment


class TestAuthenticationFlow:
    """Tests for authentication routes."""
    
    def test_index_redirect_to_login(self, client):
        """Test index redirects to login when not authenticated."""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_index_redirect_to_dashboard_when_authenticated(self, client, test_user_with_token):
        """Test index redirects to dashboard when authenticated."""
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)
            
            response = client.get('/', follow_redirects=False)
            assert response.status_code == 302
            assert '/dashboard' in response.location
    
    def test_login_page_renders(self, client):
        """Test login page renders correctly."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Strava' in response.data
    
    def test_login_redirect_when_authenticated(self, client, test_user_with_token):
        """Test login redirects to dashboard when already authenticated."""
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)
            
            response = client.get('/login', follow_redirects=False)
            assert response.status_code == 302
            assert '/dashboard' in response.location
    
    @patch('app.StravaAuth.get_authorization_url')
    def test_login_page_has_auth_url(self, mock_auth_url, client):
        """Test login page contains Strava authorization URL."""
        mock_auth_url.return_value = 'https://strava.com/oauth/authorize?client_id=test'
        
        response = client.get('/login')
        assert response.status_code == 200
        assert b'https://strava.com/oauth/authorize' in response.data
    
    @patch('app.StravaAuth.save_user_and_token')
    @patch('app.StravaAuth.exchange_code_for_token')
    def test_auth_callback_success(self, mock_exchange, mock_save, client, test_user, mock_strava_token_response):
        """Test successful OAuth callback."""
        mock_exchange.return_value = mock_strava_token_response
        mock_save.return_value = test_user
        
        response = client.get('/auth/callback?code=test_code', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Successfully logged in' in response.data
        mock_exchange.assert_called_once_with('test_code')
        mock_save.assert_called_once_with(mock_strava_token_response)
    
    def test_auth_callback_error(self, client):
        """Test OAuth callback with error parameter."""
        response = client.get('/auth/callback?error=access_denied', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Authentication error' in response.data
    
    def test_auth_callback_no_code(self, client):
        """Test OAuth callback without code parameter."""
        response = client.get('/auth/callback', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'No authorization code' in response.data
    
    @patch('app.StravaAuth.exchange_code_for_token')
    def test_auth_callback_exchange_failure(self, mock_exchange, client):
        """Test OAuth callback when token exchange fails."""
        mock_exchange.side_effect = Exception('Token exchange failed')
        
        response = client.get('/auth/callback?code=test_code', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Authentication failed' in response.data
    
    def test_logout(self, client, test_user_with_token):
        """Test logout functionality."""
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)
            
            response = client.get('/logout', follow_redirects=True)
            
            assert response.status_code == 200
            assert b'logged out' in response.data


class TestDashboard:
    """Tests for dashboard route."""
    
    def test_dashboard_requires_authentication(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    @patch('app.EquipmentService.get_equipment_with_stats')
    def test_dashboard_displays_equipment(self, mock_get_stats, client, test_user_with_token, test_equipment):
        """Test dashboard displays equipment with stats."""
        mock_get_stats.return_value = [
            {
                'equipment': test_equipment,
                'stats': {
                    'total_distance_km': 100.5,
                    'total_time_hours': 5.25,
                    'days_elapsed': 30,
                    'activity_count': 10
                }
            }
        ]
        
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)
            
            response = client.get('/dashboard')
            
            assert response.status_code == 200
            assert b'Test Chain' in response.data
            assert b'100.5' in response.data
    
    @patch('app.EquipmentService.get_equipment_with_stats')
    def test_dashboard_handles_strava_error(self, mock_get_stats, client, test_user_with_token):
        """Test dashboard handles Strava API errors gracefully."""
        mock_get_stats.side_effect = Exception('Strava API error')
        
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)
            
            response = client.get('/dashboard')
            
            assert response.status_code == 200
            assert b'Error loading dashboard' in response.data


class TestEquipmentCRUD:
    """Tests for equipment CRUD routes."""

    def test_add_equipment_get_requires_auth(self, client):
        """Test add equipment page requires authentication."""
        response = client.get('/equipment/add', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    def test_add_equipment_get_renders_form(self, client, test_user_with_token):
        """Test add equipment page renders form."""
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.get('/equipment/add')

            assert response.status_code == 200
            assert b'Add Equipment' in response.data
            assert b'name' in response.data
            assert b'equipment_type' in response.data

    @patch('app.EquipmentService.create_equipment')
    def test_add_equipment_post_success(self, mock_create, client, test_user_with_token):
        """Test adding equipment via POST."""
        mock_create.return_value = MagicMock(id=1, name='New Chain')

        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.post('/equipment/add', data={
                'name': 'New Chain',
                'equipment_type': 'Chain',
                'installation_date': '2024-01-15',
                'notes': 'Test notes'
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b'added successfully' in response.data
            mock_create.assert_called_once()

    def test_add_equipment_post_invalid_date(self, client, test_user_with_token):
        """Test adding equipment with invalid date format."""
        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.post('/equipment/add', data={
                'name': 'New Chain',
                'equipment_type': 'Chain',
                'installation_date': 'invalid-date',
                'notes': 'Test notes'
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b'Invalid date format' in response.data

    def test_edit_equipment_get_requires_auth(self, client, test_equipment):
        """Test edit equipment page requires authentication."""
        response = client.get(f'/equipment/edit/{test_equipment.id}', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    @patch('app.EquipmentService.get_equipment_by_id')
    def test_edit_equipment_get_renders_form(self, mock_get, client, test_user_with_token, test_equipment):
        """Test edit equipment page renders form with existing data."""
        mock_get.return_value = test_equipment

        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.get(f'/equipment/edit/{test_equipment.id}')

            assert response.status_code == 200
            assert b'Edit Equipment' in response.data
            assert b'Test Chain' in response.data

    @patch('app.EquipmentService.get_equipment_by_id')
    def test_edit_equipment_not_found(self, mock_get, client, test_user_with_token):
        """Test editing non-existent equipment."""
        mock_get.return_value = None

        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.get('/equipment/edit/99999', follow_redirects=True)

            assert response.status_code == 200
            assert b'Equipment not found' in response.data

    @patch('app.EquipmentService.update_equipment')
    @patch('app.EquipmentService.get_equipment_by_id')
    def test_edit_equipment_post_success(self, mock_get, mock_update, client, test_user_with_token, test_equipment):
        """Test updating equipment via POST."""
        mock_get.return_value = test_equipment
        mock_update.return_value = test_equipment

        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.post(f'/equipment/edit/{test_equipment.id}', data={
                'name': 'Updated Chain',
                'equipment_type': 'Chain',
                'installation_date': '2024-01-20',
                'notes': 'Updated notes'
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b'updated successfully' in response.data
            mock_update.assert_called_once()

    def test_delete_equipment_requires_auth(self, client, test_equipment):
        """Test delete equipment requires authentication."""
        response = client.post(f'/equipment/delete/{test_equipment.id}', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    @patch('app.EquipmentService.delete_equipment')
    def test_delete_equipment_success(self, mock_delete, client, test_user_with_token, test_equipment):
        """Test deleting equipment."""
        mock_delete.return_value = True

        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.post(f'/equipment/delete/{test_equipment.id}', follow_redirects=True)

            assert response.status_code == 200
            assert b'deleted successfully' in response.data
            mock_delete.assert_called_once_with(test_equipment.id, test_user_with_token)

    @patch('app.EquipmentService.delete_equipment')
    def test_delete_equipment_not_found(self, mock_delete, client, test_user_with_token):
        """Test deleting non-existent equipment."""
        mock_delete.return_value = False

        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            response = client.post('/equipment/delete/99999', follow_redirects=True)

            assert response.status_code == 200
            assert b'Equipment not found' in response.data

    @patch('app.EquipmentService.get_equipment_by_id')
    def test_equipment_authorization(self, mock_get, client, test_user_with_token, test_equipment):
        """Test users can only access their own equipment."""
        # Mock returns None when user doesn't own the equipment
        mock_get.return_value = None

        with client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user_with_token.id)

            # Try to edit equipment that doesn't belong to user
            response = client.get('/equipment/edit/99999', follow_redirects=True)

            assert response.status_code == 200
            assert b'Equipment not found' in response.data


