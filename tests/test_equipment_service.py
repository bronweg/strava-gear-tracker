"""
Unit tests for equipment service.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from equipment_service import EquipmentService
from models import db, Equipment, StravaBike, User


class TestEquipmentService:
    """Tests for the EquipmentService class."""
    
    def test_create_equipment(self, app, test_user):
        """Test creating equipment."""
        with app.app_context():
            equipment = EquipmentService.create_equipment(
                user=test_user,
                name='New Chain',
                equipment_type='Chain',
                installation_date=datetime(2024, 2, 1).date(),
                notes='Test notes'
            )
            
            assert equipment.id is not None
            assert equipment.name == 'New Chain'
            assert equipment.equipment_type == 'Chain'
            assert equipment.installation_date == datetime(2024, 2, 1).date()
            assert equipment.notes == 'Test notes'
            assert equipment.user_id == test_user.id
    
    def test_create_equipment_with_bike_id(self, app, test_user):
        """Test creating equipment with Strava bike ID."""
        with app.app_context():
            equipment = EquipmentService.create_equipment(
                user=test_user,
                name='Chain',
                equipment_type='Chain',
                installation_date=datetime(2024, 1, 1).date(),
                strava_bike_id='b12345'
            )
            
            assert equipment.strava_bike_id == 'b12345'
    
    def test_get_equipment_by_id(self, app, test_user, test_equipment):
        """Test getting equipment by ID."""
        with app.app_context():
            equipment = EquipmentService.get_equipment_by_id(test_equipment.id, test_user)
            
            assert equipment is not None
            assert equipment.id == test_equipment.id
            assert equipment.name == test_equipment.name
    
    def test_get_equipment_by_id_wrong_user(self, app, test_user, test_equipment):
        """Test getting equipment by ID with wrong user."""
        with app.app_context():
            # Create another user
            other_user = User(
                strava_id=99999,
                username='otheruser',
                firstname='Other',
                lastname='User'
            )
            db.session.add(other_user)
            db.session.commit()
            
            # Try to get equipment belonging to test_user
            equipment = EquipmentService.get_equipment_by_id(test_equipment.id, other_user)
            
            assert equipment is None
    
    def test_get_all_equipment(self, app, test_user):
        """Test getting all equipment for a user."""
        with app.app_context():
            # Create multiple equipment items
            eq1 = EquipmentService.create_equipment(
                user=test_user,
                name='Chain',
                equipment_type='Chain',
                installation_date=datetime(2024, 1, 1).date()
            )
            eq2 = EquipmentService.create_equipment(
                user=test_user,
                name='Tires',
                equipment_type='Tires',
                installation_date=datetime(2024, 2, 1).date()
            )
            
            equipment_list = EquipmentService.get_all_equipment(test_user)
            
            assert len(equipment_list) == 2
            # Should be ordered by installation_date desc
            assert equipment_list[0].id == eq2.id
            assert equipment_list[1].id == eq1.id
    
    def test_update_equipment(self, app, test_user, test_equipment):
        """Test updating equipment."""
        with app.app_context():
            updated = EquipmentService.update_equipment(
                equipment_id=test_equipment.id,
                user=test_user,
                name='Updated Chain',
                equipment_type='Chain - Updated',
                notes='Updated notes'
            )
            
            assert updated is not None
            assert updated.name == 'Updated Chain'
            assert updated.equipment_type == 'Chain - Updated'
            assert updated.notes == 'Updated notes'
            assert updated.installation_date == test_equipment.installation_date
    
    def test_update_equipment_partial(self, app, test_user, test_equipment):
        """Test updating equipment with partial data."""
        with app.app_context():
            original_name = test_equipment.name
            
            updated = EquipmentService.update_equipment(
                equipment_id=test_equipment.id,
                user=test_user,
                notes='Only notes updated'
            )
            
            assert updated.name == original_name
            assert updated.notes == 'Only notes updated'
    
    def test_update_equipment_wrong_user(self, app, test_user, test_equipment):
        """Test updating equipment with wrong user."""
        with app.app_context():
            # Create another user
            from models import User
            other_user = User(
                strava_id=99999,
                username='otheruser',
                firstname='Other',
                lastname='User'
            )
            db.session.add(other_user)
            db.session.commit()
            
            updated = EquipmentService.update_equipment(
                equipment_id=test_equipment.id,
                user=other_user,
                name='Hacked'
            )
            
            assert updated is None
    
    def test_update_equipment_clear_bike_id(self, app, test_user):
        """Test clearing bike ID from equipment."""
        with app.app_context():
            equipment = EquipmentService.create_equipment(
                user=test_user,
                name='Chain',
                equipment_type='Chain',
                installation_date=datetime(2024, 1, 1).date(),
                strava_bike_id='b12345'
            )

            assert equipment.strava_bike_id == 'b12345'

            # Clear the bike ID
            updated = EquipmentService.update_equipment(
                equipment_id=equipment.id,
                user=test_user,
                strava_bike_id=''
            )

            assert updated.strava_bike_id is None

    def test_delete_equipment(self, app, test_user, test_equipment):
        """Test deleting equipment."""
        with app.app_context():
            equipment_id = test_equipment.id

            result = EquipmentService.delete_equipment(equipment_id, test_user)

            assert result is True

            # Verify equipment is deleted
            deleted = Equipment.query.get(equipment_id)
            assert deleted is None

    def test_delete_equipment_wrong_user(self, app, test_user, test_equipment):
        """Test deleting equipment with wrong user."""
        with app.app_context():
            from models import User
            other_user = User(
                strava_id=99999,
                username='otheruser',
                firstname='Other',
                lastname='User'
            )
            db.session.add(other_user)
            db.session.commit()

            result = EquipmentService.delete_equipment(test_equipment.id, other_user)

            assert result is False

            # Verify equipment still exists
            equipment = Equipment.query.get(test_equipment.id)
            assert equipment is not None

    def test_delete_equipment_not_found(self, app, test_user):
        """Test deleting non-existent equipment."""
        with app.app_context():
            result = EquipmentService.delete_equipment(99999, test_user)

            assert result is False

    @patch('equipment_service.StravaService')
    def test_get_equipment_with_stats(self, mock_service_class, app, test_user, test_equipment):
        """Test getting equipment with Strava statistics."""
        with app.app_context():
            # Mock the StravaService
            mock_service = MagicMock()
            mock_service.calculate_equipment_stats_for_bike.return_value = {
                'total_distance_km': 100.5,
                'total_time_hours': 5.25,
                'days_elapsed': 30,
                'activity_count': 10
            }
            mock_service_class.return_value = mock_service

            result = EquipmentService.get_equipment_with_stats(test_user)

            assert len(result) == 1
            assert result[0]['equipment'].id == test_equipment.id
            assert result[0]['stats']['total_distance_km'] == 100.5
            assert result[0]['stats']['total_time_hours'] == 5.25
            assert result[0]['stats']['activity_count'] == 10

    @patch('equipment_service.StravaService')
    def test_get_equipment_with_stats_error_handling(self, mock_service_class, app, test_user, test_equipment):
        """Test getting equipment with stats when Strava API fails."""
        with app.app_context():
            # Mock the StravaService to raise an exception
            mock_service = MagicMock()
            mock_service.calculate_equipment_stats_for_bike.side_effect = Exception('API Error')
            mock_service_class.return_value = mock_service

            result = EquipmentService.get_equipment_with_stats(test_user)

            assert len(result) == 1
            assert result[0]['equipment'].id == test_equipment.id
            assert result[0]['stats']['total_distance_km'] == 0
            assert result[0]['stats']['total_time_hours'] == 0
            assert 'error' in result[0]['stats']
            assert 'API Error' in result[0]['stats']['error']

    @patch('equipment_service.StravaService')
    def test_sync_bikes_from_strava(self, mock_service_class, app, test_user, mock_strava_athlete):
        """Test syncing bikes from Strava."""
        with app.app_context():
            # Mock the StravaService
            mock_service = MagicMock()
            mock_service.get_athlete_bikes.return_value = mock_strava_athlete['bikes']
            mock_service_class.return_value = mock_service

            count = EquipmentService.sync_bikes_from_strava(test_user)

            assert count == 2

            # Verify bikes were created
            bikes = StravaBike.query.filter_by(user_id=test_user.id).all()
            assert len(bikes) == 2
            assert bikes[0].strava_gear_id == 'b12345'
            assert bikes[0].name == 'Trek Domane'
            assert bikes[1].strava_gear_id == 'b67890'

    @patch('equipment_service.StravaService')
    def test_sync_bikes_update_existing(self, mock_service_class, app, test_user, test_bike, mock_strava_athlete):
        """Test syncing bikes updates existing bikes."""
        with app.app_context():
            # Mock the StravaService with updated data
            updated_bikes = [
                {
                    'id': 'b12345',
                    'name': 'Updated Trek Domane',
                    'nickname': 'Updated Nickname',
                    'brand_name': 'Trek',
                    'model_name': 'Domane SL7',
                    'primary': True,
                    'distance': 75000.0
                }
            ]

            mock_service = MagicMock()
            mock_service.get_athlete_bikes.return_value = updated_bikes
            mock_service_class.return_value = mock_service

            count = EquipmentService.sync_bikes_from_strava(test_user)

            assert count == 1

            # Verify bike was updated, not duplicated
            bikes = StravaBike.query.filter_by(strava_gear_id='b12345').all()
            assert len(bikes) == 1
            assert bikes[0].name == 'Updated Trek Domane'
            assert bikes[0].nickname == 'Updated Nickname'
            assert bikes[0].distance == 75000.0

    def test_get_user_bikes(self, app, test_user, test_bike):
        """Test getting user's bikes."""
        with app.app_context():
            # Create another bike
            bike2 = StravaBike(
                user_id=test_user.id,
                strava_gear_id='b67890',
                name='Second Bike',
                primary=False,
                distance=30000.0
            )
            db.session.add(bike2)
            db.session.commit()

            bikes = EquipmentService.get_user_bikes(test_user)

            assert len(bikes) == 2
            # Should be ordered by primary desc
            assert bikes[0].primary is True
            assert bikes[1].primary is False


