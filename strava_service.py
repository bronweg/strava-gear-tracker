import requests
import time
from datetime import datetime
from flask import current_app
from strava_auth import StravaAuth


class StravaService:
    """Service for interacting with Strava API."""
    
    def __init__(self, user):
        self.user = user
        self.access_token = StravaAuth.get_valid_token(user)
        self.base_url = current_app.config['STRAVA_API_BASE_URL']
    
    def _make_request(self, endpoint, params=None):
        """Make a request to Strava API with rate limiting handling."""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        url = f'{self.base_url}/{endpoint}'
        
        response = requests.get(url, headers=headers, params=params)
        
        # Handle rate limiting
        if response.status_code == 429:
            # Rate limit exceeded, wait and retry
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f'Strava API error: {response.status_code} - {response.text}')
        
        return response.json()
    
    def get_activities_since(self, start_date, end_date=None):
        """
        Fetch all activities since a given date.
        
        Args:
            start_date: datetime.date object for the start date
            end_date: datetime.date object for the end date (default: today)
        
        Returns:
            List of activity dictionaries
        """
        if end_date is None:
            end_date = datetime.now().date()
        
        # Convert dates to Unix timestamps
        after = int(datetime.combine(start_date, datetime.min.time()).timestamp())
        before = int(datetime.combine(end_date, datetime.max.time()).timestamp())
        
        all_activities = []
        page = 1
        per_page = 200  # Maximum allowed by Strava API
        
        while True:
            params = {
                'after': after,
                'before': before,
                'page': page,
                'per_page': per_page
            }
            
            activities = self._make_request('athlete/activities', params)
            
            if not activities:
                break
            
            all_activities.extend(activities)
            
            # If we got fewer activities than per_page, we've reached the end
            if len(activities) < per_page:
                break
            
            page += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        return all_activities
    
    def calculate_equipment_stats(self, installation_date):
        """
        Calculate statistics for equipment installed on a given date.
        
        Args:
            installation_date: datetime.date object
        
        Returns:
            Dictionary with total_distance_km, total_time_hours, days_elapsed
        """
        activities = self.get_activities_since(installation_date)
        
        # Filter for ride activities only (excluding virtual rides)
        ride_activities = [a for a in activities if a.get('type') in ['Ride', 'EBikeRide']]
        
        total_distance_meters = sum(a.get('distance', 0) for a in ride_activities)
        total_time_seconds = sum(a.get('moving_time', 0) for a in ride_activities)
        
        total_distance_km = total_distance_meters / 1000
        total_time_hours = total_time_seconds / 3600
        
        days_elapsed = (datetime.now().date() - installation_date).days
        
        return {
            'total_distance_km': round(total_distance_km, 2),
            'total_time_hours': round(total_time_hours, 2),
            'days_elapsed': days_elapsed,
            'activity_count': len(ride_activities)
        }
    
    def get_athlete_info(self):
        """Get current athlete information."""
        return self._make_request('athlete')

    def get_athlete_bikes(self):
        """
        Fetch the athlete's bikes/gear from Strava.

        Returns:
            List of bike dictionaries with id, name, nickname, brand_name, model_name, etc.
        """
        athlete_data = self.get_athlete_info()
        bikes = athlete_data.get('bikes', [])
        return bikes

    def calculate_equipment_stats_for_bike(self, installation_date, strava_bike_id=None):
        """
        Calculate statistics for equipment installed on a given date, optionally filtered by bike.

        Args:
            installation_date: datetime.date object
            strava_bike_id: Optional Strava gear ID to filter activities by specific bike

        Returns:
            Dictionary with total_distance_km, total_time_hours, days_elapsed, activity_count
        """
        activities = self.get_activities_since(installation_date)

        # Filter for ride activities only (excluding virtual rides)
        ride_activities = [a for a in activities if a.get('type') in ['Ride', 'EBikeRide']]

        # If strava_bike_id is specified, filter activities for that specific bike
        if strava_bike_id:
            ride_activities = [a for a in ride_activities if a.get('gear_id') == strava_bike_id]

        total_distance_meters = sum(a.get('distance', 0) for a in ride_activities)
        total_time_seconds = sum(a.get('moving_time', 0) for a in ride_activities)

        total_distance_km = total_distance_meters / 1000
        total_time_hours = total_time_seconds / 3600

        days_elapsed = (datetime.now().date() - installation_date).days

        return {
            'total_distance_km': round(total_distance_km, 2),
            'total_time_hours': round(total_time_hours, 2),
            'days_elapsed': days_elapsed,
            'activity_count': len(ride_activities)
        }

