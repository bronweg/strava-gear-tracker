# Test Suite for Bike Equipment Tracker

This directory contains comprehensive unit and integration tests for the Bike Equipment Tracker application.

## Test Structure

```
tests/
├── __init__.py                    # Tests package initialization
├── conftest.py                    # Shared pytest fixtures
├── test_models.py                 # Unit tests for database models
├── test_strava_auth.py           # Unit tests for Strava authentication
├── test_strava_service.py        # Unit tests for Strava service
├── test_equipment_service.py     # Unit tests for equipment service
└── test_app.py                   # Integration tests for Flask routes
```

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_models.py
```

### Run specific test class
```bash
pytest tests/test_models.py::TestUserModel
```

### Run specific test function
```bash
pytest tests/test_models.py::TestUserModel::test_create_user
```

### Run only unit tests
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

### Run with verbose output
```bash
pytest -v
```

### Generate HTML coverage report
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Coverage

The test suite covers:

### Unit Tests

#### `test_models.py` - Database Models
- **User Model**: Creation, relationships, cascade delete
- **Equipment Model**: Creation, validation, days_since_installation()
- **StravaToken Model**: Creation, is_expired() logic, unique constraints
- **StravaBike Model**: Creation, display_name() method, unique constraints

#### `test_strava_auth.py` - Strava Authentication
- **get_authorization_url()**: URL generation with correct parameters
- **exchange_code_for_token()**: Successful exchange and error handling
- **refresh_access_token()**: Token refresh logic
- **save_user_and_token()**: User and token persistence (new and existing users)
- **get_valid_token()**: Token validation and automatic refresh

#### `test_strava_service.py` - Strava API Service
- **_make_request()**: API requests, rate limiting (429), error handling
- **get_activities_since()**: Activity fetching with pagination and date filtering
- **calculate_equipment_stats()**: Statistics calculation for ride activities
- **get_athlete_info()**: Athlete information retrieval
- **get_athlete_bikes()**: Bikes/gear retrieval
- **calculate_equipment_stats_for_bike()**: Bike-specific statistics

#### `test_equipment_service.py` - Equipment Service
- **create_equipment()**: Equipment creation with and without bike ID
- **get_all_equipment()**: Retrieving user's equipment
- **get_equipment_by_id()**: Single equipment retrieval and authorization
- **update_equipment()**: Equipment updates and authorization
- **delete_equipment()**: Equipment deletion and authorization
- **get_equipment_with_stats()**: Equipment with Strava stats and error handling
- **sync_bikes_from_strava()**: Syncing bikes from Strava API
- **get_user_bikes()**: Retrieving user's bikes

### Integration Tests

#### `test_app.py` - Flask Application Routes

**Authentication Flow**:
- Login page rendering
- Strava OAuth redirect
- OAuth callback (success and error cases)
- Logout functionality

**Dashboard**:
- Authentication requirement
- Equipment display with statistics
- Error handling for Strava API failures

**Equipment CRUD**:
- Add equipment (GET/POST)
- Edit equipment (GET/POST)
- Delete equipment
- Authorization (users can only access their own equipment)
- Input validation (date format, etc.)

## Fixtures

### Database Fixtures
- `app`: Test Flask application with in-memory SQLite database
- `client`: Test client for making HTTP requests
- `test_user`: Basic test user
- `test_user_with_token`: Test user with valid Strava token
- `test_equipment`: Test equipment item
- `test_bike`: Test Strava bike

### Mock Data Fixtures
- `mock_strava_token_response`: Mock OAuth token response
- `mock_strava_activities`: Mock activities data (Ride, VirtualRide, EBikeRide)
- `mock_strava_athlete`: Mock athlete info with bikes
- `mock_rate_limit_response`: Mock 429 rate limit response
- `mock_error_response`: Mock error response
- `mock_success_response`: Mock successful response

## Mocking Strategy

All external API calls to Strava are mocked using `unittest.mock.patch`:

1. **OAuth endpoints**: Token exchange and refresh
2. **Activity endpoints**: Activities with pagination
3. **Athlete endpoints**: Athlete info and bikes
4. **Rate limiting**: 429 responses with Retry-After headers

This ensures tests:
- Run quickly without network calls
- Are deterministic and reliable
- Don't depend on external services
- Can test error scenarios

## Best Practices

1. **Isolation**: Each test is independent and doesn't affect others
2. **In-memory database**: Tests use SQLite in-memory for speed
3. **Mocking**: All external dependencies are mocked
4. **Coverage**: Aim for >80% code coverage
5. **Naming**: Test names clearly describe what they test
6. **Assertions**: Each test has clear, specific assertions

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run tests with coverage
pytest --cov=. --cov-report=xml --cov-report=term

# Check coverage threshold (optional)
pytest --cov=. --cov-fail-under=80
```

## Troubleshooting

### Import errors
Make sure you're running pytest from the project root directory.

### Database errors
The test suite uses an in-memory SQLite database that's created fresh for each test.

### Mock not working
Ensure the patch path matches the import path in the module being tested, not where the function is defined.

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve code coverage
4. Follow existing test patterns and naming conventions

