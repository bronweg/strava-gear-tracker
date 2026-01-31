# Changelog

All notable changes to the Bike Equipment Tracker project will be documented in this file.

## [1.2.0] - 2026-01-30

### Added

#### Multi-Bike Support
- **Bike Syncing**: Automatically fetch and store bikes from Strava API
- **Bike Association**: Equipment can now be associated with specific bikes
- **Bike-Specific Tracking**: Activities are filtered by bike when equipment is bike-specific
- **Bike Display**: Show bike name/nickname in dashboard and equipment forms

#### New Database Model
- **StravaBike Model**: New model to store Strava bikes/gear information
  - Fields: strava_gear_id, name, nickname, brand_name, model_name, primary, distance
  - Relationship with User model
  - `display_name()` method for smart name display

#### Enhanced Equipment Model
- **strava_bike_id Field**: Optional field to associate equipment with specific bikes
- **Bike Relationship**: Relationship to StravaBike model for easy access
- **Backward Compatible**: Null strava_bike_id means "all bikes" (existing behavior)

#### Enhanced Strava Service
- **get_athlete_bikes()**: Fetch bikes from Strava API
- **calculate_equipment_stats_for_bike()**: Calculate stats with optional bike filtering
- **Bike Filtering**: Filter activities by gear_id when bike is specified

#### Enhanced Equipment Service
- **sync_bikes_from_strava()**: Sync bikes from Strava to local database
- **get_user_bikes()**: Get all bikes for a user
- **Updated CRUD**: create_equipment() and update_equipment() now support strava_bike_id parameter

#### Updated Flask Routes
- **Dashboard**: Automatically syncs bikes on load
- **Add Equipment**: Bike selection dropdown with user's bikes
- **Edit Equipment**: Bike selection dropdown with current bike pre-selected
- **Bike Data**: All routes pass bike list to templates

#### Updated Templates
- **add_equipment.html**: Bike selection dropdown with "All bikes" option
- **edit_equipment.html**: Bike selection dropdown with current selection
- **dashboard.html**: Display bike name for each equipment item
- **Help Text**: Updated "How it works" sections to explain bike-specific tracking

### Changed

- Equipment statistics now respect bike associations
- Dashboard shows which bike each equipment is associated with
- Forms include bike selection for better equipment organization

### Technical Details

**New Files**: None (all changes to existing files)

**Database Changes**:
- New table: `strava_bikes`
- New column in `equipment` table: `strava_bike_id` (nullable)
- New relationship: User.bikes

**API Changes**:
- Now calls `GET /athlete` endpoint to fetch bikes
- Activities filtered by `gear_id` when bike is specified

### Backward Compatibility

✅ **Fully Backward Compatible**:
- Existing equipment without `strava_bike_id` continues to work
- Null `strava_bike_id` means "all bikes" (counts all activities)
- No data migration required
- Existing users won't see any breaking changes

---

## [1.1.0] - 2026-01-30

### Changed

#### Activity Filtering Enhancement
- **Modified `strava_service.py`**: Updated activity filtering to exclude VirtualRide activities from equipment statistics calculation
- **Rationale**: Virtual/indoor rides (e.g., Zwift, TrainerRoad) don't cause wear on outdoor bicycle components like chains, tires, cassettes, and other equipment

#### Activity Types Now Tracked
- ✅ **Ride**: Outdoor bicycle rides
- ✅ **EBikeRide**: Electric bicycle rides
- ❌ **VirtualRide**: Excluded (indoor/virtual rides)

#### Documentation Updates
Updated all documentation files to reflect the activity filtering change:

1. **PROJECT_SUMMARY.md**
   - Updated "Activity Types Tracked" section
   - Added detailed explanation of why VirtualRide activities are excluded
   - Clarified that only outdoor rides affect equipment wear

2. **README.md**
   - Updated "Features" section to mention smart filtering
   - Added "Activity Filtering" subsection in "Technical Details"
   - Updated "Viewing Statistics" section to clarify outdoor rides only
   - Added notes explaining the rationale for excluding virtual rides

3. **QUICKSTART.md**
   - Updated Step 7 to clarify that only outdoor rides are fetched
   - Added note explaining virtual ride exclusion

4. **templates/add_equipment.html**
   - Updated "How it works" section to specify outdoor rides only
   - Added explanation about virtual ride exclusion

5. **templates/login.html**
   - Updated feature list to mention "outdoor rides" and "outdoor activities"

### Technical Details

**Code Change Location**: `strava_service.py`, line 96

**Before**:
```python
ride_activities = [a for a in activities if a.get('type') in ['Ride', 'VirtualRide', 'EBikeRide']]
```

**After**:
```python
ride_activities = [a for a in activities if a.get('type') in ['Ride', 'EBikeRide']]
```

### Impact

- Equipment statistics now more accurately reflect actual outdoor component wear
- Users who do indoor training won't see inflated equipment usage numbers
- Better alignment with real-world equipment maintenance needs

---

## [1.0.0] - 2026-01-30

### Added

#### Initial Release
- Complete bicycle equipment tracking application
- Strava OAuth 2.0 integration
- Equipment CRUD operations
- Automatic statistics calculation
- Responsive web interface
- SQLite database storage
- Comprehensive documentation
- Automated setup scripts

#### Features
- User authentication via Strava
- Equipment management (add, edit, delete)
- Automatic activity fetching from Strava API
- Statistics calculation (distance, time, days)
- Rate limit handling
- Token refresh automation
- Error handling

#### Documentation
- README.md with full documentation
- QUICKSTART.md for fast setup
- DEPLOYMENT.md for production deployment
- PROJECT_SUMMARY.md for project overview
- Automated setup scripts for Unix and Windows

#### Technical Stack
- Python 3.8+
- Flask 3.0
- SQLAlchemy
- Flask-Login
- Strava API v3
- Bootstrap 5

