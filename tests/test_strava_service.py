"""
Unit tests for Strava service.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import time
from strava_service import StravaService


class TestStravaService:
    """Tests for the StravaService class."""
    
    @patch('strava_service.StravaAuth.get_valid_token')
    def test_init(self, mock_get_token, app, test_user_with_token):
        """Test StravaService initialization."""
        mock_get_token.return_value = 'test_access_token'
        
        with app.app_context():
            service = StravaService(test_user_with_token)
            
            assert service.user == test_user_with_token
            assert service.access_token == 'test_access_token'
            assert service.base_url == 'https://www.strava.com/api/v3'
    
    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.requests.get')
    def test_make_request_success(self, mock_get, mock_get_token, app, test_user_with_token):
        """Test successful API request."""
        mock_get_token.return_value = 'test_access_token'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        with app.app_context():
            service = StravaService(test_user_with_token)
            result = service._make_request('athlete')
            
            assert result == {'data': 'test'}
            mock_get.assert_called_once()
            
            # Verify headers
            call_args = mock_get.call_args
            assert call_args[1]['headers']['Authorization'] == 'Bearer test_access_token'
    
    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.requests.get')
    def test_make_request_with_params(self, mock_get, mock_get_token, app, test_user_with_token):
        """Test API request with parameters."""
        mock_get_token.return_value = 'test_access_token'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        with app.app_context():
            service = StravaService(test_user_with_token)
            params = {'page': 1, 'per_page': 200}
            service._make_request('athlete/activities', params)
            
            # Verify params were passed
            call_args = mock_get.call_args
            assert call_args[1]['params'] == params
    
    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.requests.get')
    @patch('strava_service.time.sleep')
    def test_make_request_rate_limit(self, mock_sleep, mock_get, mock_get_token, app, test_user_with_token):
        """Test API request with rate limiting (429 status)."""
        mock_get_token.return_value = 'test_access_token'
        
        # First response: rate limited
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {'Retry-After': '2'}
        
        # Second response: success
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {'data': 'success'}
        
        mock_get.side_effect = [rate_limit_response, success_response]
        
        with app.app_context():
            service = StravaService(test_user_with_token)
            result = service._make_request('athlete')
            
            assert result == {'data': 'success'}
            assert mock_get.call_count == 2
            mock_sleep.assert_called_once_with(2)
    
    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.requests.get')
    def test_make_request_error(self, mock_get, mock_get_token, app, test_user_with_token):
        """Test API request with error response."""
        mock_get_token.return_value = 'test_access_token'
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_get.return_value = mock_response
        
        with app.app_context():
            service = StravaService(test_user_with_token)
            
            with pytest.raises(Exception) as exc_info:
                service._make_request('athlete')
            
            assert 'Strava API error: 401' in str(exc_info.value)
    
    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService._make_request')
    def test_get_activities_since_single_page(self, mock_request, mock_get_token, app, test_user_with_token, mock_strava_activities):
        """Test fetching activities with single page of results."""
        mock_get_token.return_value = 'test_access_token'
        mock_request.return_value = mock_strava_activities
        
        with app.app_context():
            service = StravaService(test_user_with_token)
            start_date = datetime(2024, 1, 1).date()
            
            activities = service.get_activities_since(start_date)
            
            assert len(activities) == 4
            assert activities == mock_strava_activities
            mock_request.assert_called_once()
    
    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService._make_request')
    @patch('strava_service.time.sleep')
    def test_get_activities_since_multiple_pages(self, mock_sleep, mock_request, mock_get_token, app, test_user_with_token):
        """Test fetching activities with pagination."""
        mock_get_token.return_value = 'test_access_token'
        
        # Create mock data for multiple pages
        page1 = [{'id': i} for i in range(200)]  # Full page
        page2 = [{'id': i} for i in range(200, 250)]  # Partial page (50 items)
        
        mock_request.side_effect = [page1, page2]
        
        with app.app_context():
            service = StravaService(test_user_with_token)
            start_date = datetime(2024, 1, 1).date()
            
            activities = service.get_activities_since(start_date)
            
            assert len(activities) == 250
            assert mock_request.call_count == 2
            
            # Verify pagination parameters
            calls = mock_request.call_args_list
            assert calls[0][0][1]['page'] == 1
            assert calls[1][0][1]['page'] == 2

    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService._make_request')
    def test_get_activities_since_with_date_range(self, mock_request, mock_get_token, app, test_user_with_token):
        """Test fetching activities with start and end dates."""
        mock_get_token.return_value = 'test_access_token'
        mock_request.return_value = []

        with app.app_context():
            service = StravaService(test_user_with_token)
            start_date = datetime(2024, 1, 1).date()
            end_date = datetime(2024, 1, 31).date()

            service.get_activities_since(start_date, end_date)

            # Verify date parameters
            call_args = mock_request.call_args
            params = call_args[0][1]

            # Verify timestamps are within expected range
            assert params['after'] > 0
            assert params['before'] > params['after']

    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService.get_activities_since')
    def test_calculate_equipment_stats(self, mock_get_activities, mock_get_token, app, test_user_with_token, mock_strava_activities):
        """Test calculating equipment statistics."""
        mock_get_token.return_value = 'test_access_token'
        mock_get_activities.return_value = mock_strava_activities

        with app.app_context():
            service = StravaService(test_user_with_token)
            install_date = datetime(2024, 1, 1).date()

            stats = service.calculate_equipment_stats(install_date)

            # Expected: 2 Ride activities (10km + 15km) + 1 EBikeRide (12km) = 37km
            # VirtualRide should be excluded
            assert stats['total_distance_km'] == 37.0

            # Expected: 1800s + 2700s + 2400s = 6900s = 1.92 hours
            assert stats['total_time_hours'] == 1.92

            # Activity count should be 3 (2 Ride + 1 EBikeRide)
            assert stats['activity_count'] == 3

            # Days elapsed should be calculated
            assert stats['days_elapsed'] >= 0

    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService.get_activities_since')
    def test_calculate_equipment_stats_no_activities(self, mock_get_activities, mock_get_token, app, test_user_with_token):
        """Test calculating stats with no activities."""
        mock_get_token.return_value = 'test_access_token'
        mock_get_activities.return_value = []

        with app.app_context():
            service = StravaService(test_user_with_token)
            install_date = datetime(2024, 1, 1).date()

            stats = service.calculate_equipment_stats(install_date)

            assert stats['total_distance_km'] == 0.0
            assert stats['total_time_hours'] == 0.0
            assert stats['activity_count'] == 0

    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService._make_request')
    def test_get_athlete_info(self, mock_request, mock_get_token, app, test_user_with_token, mock_strava_athlete):
        """Test getting athlete information."""
        mock_get_token.return_value = 'test_access_token'
        mock_request.return_value = mock_strava_athlete

        with app.app_context():
            service = StravaService(test_user_with_token)
            athlete = service.get_athlete_info()

            assert athlete['id'] == 12345
            assert athlete['username'] == 'testuser'
            assert 'bikes' in athlete
            mock_request.assert_called_once_with('athlete')

    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService.get_athlete_info')
    def test_get_athlete_bikes(self, mock_get_athlete, mock_get_token, app, test_user_with_token, mock_strava_athlete):
        """Test getting athlete's bikes."""
        mock_get_token.return_value = 'test_access_token'
        mock_get_athlete.return_value = mock_strava_athlete

        with app.app_context():
            service = StravaService(test_user_with_token)
            bikes = service.get_athlete_bikes()

            assert len(bikes) == 2
            assert bikes[0]['id'] == 'b12345'
            assert bikes[0]['name'] == 'Trek Domane'
            assert bikes[1]['id'] == 'b67890'

    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService.get_activities_since')
    def test_calculate_equipment_stats_for_bike(self, mock_get_activities, mock_get_token, app, test_user_with_token, mock_strava_activities):
        """Test calculating stats filtered by bike."""
        mock_get_token.return_value = 'test_access_token'
        mock_get_activities.return_value = mock_strava_activities

        with app.app_context():
            service = StravaService(test_user_with_token)
            install_date = datetime(2024, 1, 1).date()

            # Filter by specific bike
            stats = service.calculate_equipment_stats_for_bike(install_date, 'b12345')

            # All activities have gear_id='b12345' except VirtualRide
            # Expected: 10km + 15km + 12km = 37km
            assert stats['total_distance_km'] == 37.0
            assert stats['activity_count'] == 3

    @patch('strava_service.StravaAuth.get_valid_token')
    @patch('strava_service.StravaService.get_activities_since')
    def test_calculate_equipment_stats_for_bike_no_match(self, mock_get_activities, mock_get_token, app, test_user_with_token, mock_strava_activities):
        """Test calculating stats for bike with no matching activities."""
        mock_get_token.return_value = 'test_access_token'
        mock_get_activities.return_value = mock_strava_activities

        with app.app_context():
            service = StravaService(test_user_with_token)
            install_date = datetime(2024, 1, 1).date()

            # Filter by non-existent bike
            stats = service.calculate_equipment_stats_for_bike(install_date, 'b99999')

            assert stats['total_distance_km'] == 0.0
            assert stats['total_time_hours'] == 0.0
            assert stats['activity_count'] == 0


