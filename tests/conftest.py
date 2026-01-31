"""
Shared pytest fixtures for testing the Bike Equipment Tracker application.
"""
import pytest
from datetime import datetime, timedelta
from flask import Flask
from models import db, User, Equipment, StravaToken, StravaBike
from config import Config


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    STRAVA_CLIENT_ID = 'test_client_id'
    STRAVA_CLIENT_SECRET = 'test_client_secret'
    STRAVA_REDIRECT_URI = 'http://localhost:5000/auth/callback'


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    from app import app as flask_app
    
    flask_app.config.from_object(TestConfig)
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(
        strava_id=12345,
        username='testuser',
        firstname='Test',
        lastname='User',
        profile_picture='http://example.com/profile.jpg'
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_user_with_token(app, test_user):
    """Create a test user with a valid Strava token."""
    expires_at = int((datetime.utcnow() + timedelta(hours=6)).timestamp())
    token = StravaToken(
        user_id=test_user.id,
        access_token='test_access_token',
        refresh_token='test_refresh_token',
        expires_at=expires_at
    )
    db.session.add(token)
    db.session.commit()
    return test_user


@pytest.fixture
def test_equipment(app, test_user):
    """Create test equipment."""
    equipment = Equipment(
        user_id=test_user.id,
        name='Test Chain',
        equipment_type='Chain',
        installation_date=datetime(2024, 1, 1).date(),
        notes='Test notes'
    )
    db.session.add(equipment)
    db.session.commit()
    return equipment


@pytest.fixture
def test_bike(app, test_user):
    """Create a test Strava bike."""
    bike = StravaBike(
        user_id=test_user.id,
        strava_gear_id='b12345',
        name='Test Bike',
        nickname='My Bike',
        brand_name='Trek',
        model_name='Domane',
        primary=True,
        distance=50000.0
    )
    db.session.add(bike)
    db.session.commit()
    return bike


@pytest.fixture
def mock_strava_token_response():
    """Mock Strava OAuth token response."""
    return {
        'token_type': 'Bearer',
        'expires_at': int((datetime.utcnow() + timedelta(hours=6)).timestamp()),
        'expires_in': 21600,
        'refresh_token': 'mock_refresh_token',
        'access_token': 'mock_access_token',
        'athlete': {
            'id': 12345,
            'username': 'testuser',
            'firstname': 'Test',
            'lastname': 'User',
            'profile': 'http://example.com/profile.jpg'
        }
    }


@pytest.fixture
def mock_strava_activities():
    """Mock Strava activities response."""
    return [
        {
            'id': 1,
            'name': 'Morning Ride',
            'type': 'Ride',
            'distance': 10000.0,  # 10 km in meters
            'moving_time': 1800,  # 30 minutes in seconds
            'start_date': '2024-01-15T08:00:00Z',
            'gear_id': 'b12345'
        },
        {
            'id': 2,
            'name': 'Evening Ride',
            'type': 'Ride',
            'distance': 15000.0,  # 15 km
            'moving_time': 2700,  # 45 minutes
            'start_date': '2024-01-16T18:00:00Z',
            'gear_id': 'b12345'
        },
        {
            'id': 3,
            'name': 'Virtual Ride',
            'type': 'VirtualRide',
            'distance': 20000.0,  # Should be excluded from stats
            'moving_time': 3600,
            'start_date': '2024-01-17T19:00:00Z'
        },
        {
            'id': 4,
            'name': 'E-Bike Ride',
            'type': 'EBikeRide',
            'distance': 12000.0,  # 12 km
            'moving_time': 2400,  # 40 minutes
            'start_date': '2024-01-18T10:00:00Z',
            'gear_id': 'b12345'
        }
    ]


@pytest.fixture
def mock_strava_athlete():
    """Mock Strava athlete info response."""
    return {
        'id': 12345,
        'username': 'testuser',
        'firstname': 'Test',
        'lastname': 'User',
        'profile': 'http://example.com/profile.jpg',
        'bikes': [
            {
                'id': 'b12345',
                'name': 'Trek Domane',
                'nickname': 'My Bike',
                'brand_name': 'Trek',
                'model_name': 'Domane',
                'primary': True,
                'distance': 50000.0
            },
            {
                'id': 'b67890',
                'name': 'Specialized Roubaix',
                'nickname': 'Road Bike',
                'brand_name': 'Specialized',
                'model_name': 'Roubaix',
                'primary': False,
                'distance': 30000.0
            }
        ]
    }


@pytest.fixture
def mock_rate_limit_response():
    """Mock Strava rate limit response (429)."""
    class MockResponse:
        status_code = 429
        headers = {'Retry-After': '1'}
        text = 'Rate limit exceeded'

        def json(self):
            return {'message': 'Rate limit exceeded'}

    return MockResponse()


@pytest.fixture
def mock_error_response():
    """Mock Strava error response."""
    class MockResponse:
        status_code = 401
        text = 'Unauthorized'

        def json(self):
            return {'message': 'Unauthorized', 'errors': [{'code': 'invalid'}]}

    return MockResponse()


@pytest.fixture
def mock_success_response():
    """Mock successful Strava API response."""
    class MockResponse:
        status_code = 200

        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    return MockResponse


