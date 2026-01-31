"""
Unit tests for database models.
"""
import pytest
from datetime import datetime, timedelta
from models import db, User, Equipment, StravaToken, StravaBike


class TestUserModel:
    """Tests for the User model."""
    
    def test_create_user(self, app):
        """Test creating a user."""
        user = User(
            strava_id=99999,
            username='newuser',
            firstname='New',
            lastname='User',
            profile_picture='http://example.com/pic.jpg'
        )
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.strava_id == 99999
        assert user.username == 'newuser'
        assert user.firstname == 'New'
        assert user.lastname == 'User'
        assert user.created_at is not None
    
    def test_user_repr(self, test_user):
        """Test user string representation."""
        assert repr(test_user) == '<User testuser>'
    
    def test_user_equipment_relationship(self, app, test_user):
        """Test user-equipment relationship."""
        equipment1 = Equipment(
            user_id=test_user.id,
            name='Chain',
            equipment_type='Chain',
            installation_date=datetime(2024, 1, 1).date()
        )
        equipment2 = Equipment(
            user_id=test_user.id,
            name='Tires',
            equipment_type='Tires',
            installation_date=datetime(2024, 2, 1).date()
        )
        db.session.add_all([equipment1, equipment2])
        db.session.commit()
        
        assert len(test_user.equipment) == 2
        assert equipment1 in test_user.equipment
        assert equipment2 in test_user.equipment
    
    def test_user_token_relationship(self, app, test_user):
        """Test user-token relationship."""
        token = StravaToken(
            user_id=test_user.id,
            access_token='token123',
            refresh_token='refresh123',
            expires_at=int(datetime.utcnow().timestamp()) + 3600
        )
        db.session.add(token)
        db.session.commit()
        
        assert test_user.strava_token is not None
        assert test_user.strava_token.access_token == 'token123'
    
    def test_user_cascade_delete(self, app, test_user):
        """Test that deleting a user cascades to equipment and token."""
        equipment = Equipment(
            user_id=test_user.id,
            name='Chain',
            equipment_type='Chain',
            installation_date=datetime(2024, 1, 1).date()
        )
        token = StravaToken(
            user_id=test_user.id,
            access_token='token123',
            refresh_token='refresh123',
            expires_at=int(datetime.utcnow().timestamp()) + 3600
        )
        db.session.add_all([equipment, token])
        db.session.commit()
        
        user_id = test_user.id
        db.session.delete(test_user)
        db.session.commit()
        
        # Verify equipment and token are deleted
        assert Equipment.query.filter_by(user_id=user_id).first() is None
        assert StravaToken.query.filter_by(user_id=user_id).first() is None


class TestEquipmentModel:
    """Tests for the Equipment model."""
    
    def test_create_equipment(self, app, test_user):
        """Test creating equipment."""
        equipment = Equipment(
            user_id=test_user.id,
            name='New Chain',
            equipment_type='Chain',
            installation_date=datetime(2024, 3, 1).date(),
            notes='Brand new chain'
        )
        db.session.add(equipment)
        db.session.commit()
        
        assert equipment.id is not None
        assert equipment.name == 'New Chain'
        assert equipment.equipment_type == 'Chain'
        assert equipment.notes == 'Brand new chain'
        assert equipment.created_at is not None
        assert equipment.updated_at is not None
    
    def test_equipment_repr(self, test_equipment):
        """Test equipment string representation."""
        assert repr(test_equipment) == '<Equipment Test Chain>'
    
    def test_days_since_installation(self, app, test_user):
        """Test days_since_installation calculation."""
        # Equipment installed 10 days ago
        install_date = (datetime.now() - timedelta(days=10)).date()
        equipment = Equipment(
            user_id=test_user.id,
            name='Chain',
            equipment_type='Chain',
            installation_date=install_date
        )
        db.session.add(equipment)
        db.session.commit()
        
        days = equipment.days_since_installation()
        assert days == 10
    
    def test_equipment_with_bike_id(self, app, test_user):
        """Test equipment with Strava bike ID."""
        equipment = Equipment(
            user_id=test_user.id,
            name='Chain',
            equipment_type='Chain',
            installation_date=datetime(2024, 1, 1).date(),
            strava_bike_id='b12345'
        )
        db.session.add(equipment)
        db.session.commit()
        
        assert equipment.strava_bike_id == 'b12345'


class TestStravaTokenModel:
    """Tests for the StravaToken model."""

    def test_create_token(self, app, test_user):
        """Test creating a Strava token."""
        expires_at = int((datetime.utcnow() + timedelta(hours=6)).timestamp())
        token = StravaToken(
            user_id=test_user.id,
            access_token='access123',
            refresh_token='refresh123',
            expires_at=expires_at
        )
        db.session.add(token)
        db.session.commit()

        assert token.id is not None
        assert token.access_token == 'access123'
        assert token.refresh_token == 'refresh123'
        assert token.expires_at == expires_at
        assert token.created_at is not None

    def test_token_repr(self, app, test_user):
        """Test token string representation."""
        token = StravaToken(
            user_id=test_user.id,
            access_token='access123',
            refresh_token='refresh123',
            expires_at=int(datetime.utcnow().timestamp()) + 3600
        )
        db.session.add(token)
        db.session.commit()

        assert repr(token) == f'<StravaToken for user_id={test_user.id}>'

    def test_is_expired_false(self, app, test_user):
        """Test is_expired returns False for valid token."""
        # Token expires in 6 hours
        expires_at = int((datetime.utcnow() + timedelta(hours=6)).timestamp())
        token = StravaToken(
            user_id=test_user.id,
            access_token='access123',
            refresh_token='refresh123',
            expires_at=expires_at
        )
        db.session.add(token)
        db.session.commit()

        assert token.is_expired() is False

    def test_is_expired_true(self, app, test_user):
        """Test is_expired returns True for expired token."""
        # Token expired 1 hour ago
        expires_at = int((datetime.utcnow() - timedelta(hours=1)).timestamp())
        token = StravaToken(
            user_id=test_user.id,
            access_token='access123',
            refresh_token='refresh123',
            expires_at=expires_at
        )
        db.session.add(token)
        db.session.commit()

        assert token.is_expired() is True

    def test_unique_user_constraint(self, app, test_user):
        """Test that a user can only have one token."""
        token1 = StravaToken(
            user_id=test_user.id,
            access_token='access1',
            refresh_token='refresh1',
            expires_at=int(datetime.utcnow().timestamp()) + 3600
        )
        db.session.add(token1)
        db.session.commit()

        # Try to add another token for the same user
        token2 = StravaToken(
            user_id=test_user.id,
            access_token='access2',
            refresh_token='refresh2',
            expires_at=int(datetime.utcnow().timestamp()) + 3600
        )
        db.session.add(token2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()


class TestStravaBikeModel:
    """Tests for the StravaBike model."""

    def test_create_bike(self, app, test_user):
        """Test creating a Strava bike."""
        bike = StravaBike(
            user_id=test_user.id,
            strava_gear_id='b99999',
            name='New Bike',
            nickname='My New Bike',
            brand_name='Specialized',
            model_name='Tarmac',
            primary=True,
            distance=10000.0
        )
        db.session.add(bike)
        db.session.commit()

        assert bike.id is not None
        assert bike.strava_gear_id == 'b99999'
        assert bike.name == 'New Bike'
        assert bike.nickname == 'My New Bike'
        assert bike.brand_name == 'Specialized'
        assert bike.model_name == 'Tarmac'
        assert bike.primary is True
        assert bike.distance == 10000.0

    def test_bike_repr(self, test_bike):
        """Test bike string representation."""
        # repr uses name first, then nickname
        assert repr(test_bike) == '<StravaBike Test Bike>'

    def test_display_name_with_nickname(self, test_bike):
        """Test display_name returns nickname when available."""
        assert test_bike.display_name() == 'My Bike'

    def test_display_name_with_name_only(self, app, test_user):
        """Test display_name returns name when no nickname."""
        bike = StravaBike(
            user_id=test_user.id,
            strava_gear_id='b88888',
            name='Trek Bike',
            brand_name='Trek',
            model_name='Domane'
        )
        db.session.add(bike)
        db.session.commit()

        assert bike.display_name() == 'Trek Bike'

    def test_display_name_with_brand_model(self, app, test_user):
        """Test display_name returns brand + model when no name/nickname."""
        bike = StravaBike(
            user_id=test_user.id,
            strava_gear_id='b77777',
            brand_name='Cannondale',
            model_name='SuperSix'
        )
        db.session.add(bike)
        db.session.commit()

        assert bike.display_name() == 'Cannondale SuperSix'

    def test_display_name_fallback(self, app, test_user):
        """Test display_name fallback to gear ID."""
        bike = StravaBike(
            user_id=test_user.id,
            strava_gear_id='b66666'
        )
        db.session.add(bike)
        db.session.commit()

        assert bike.display_name() == 'Bike b66666'

    def test_unique_gear_id_constraint(self, app, test_user):
        """Test that strava_gear_id must be unique."""
        bike1 = StravaBike(
            user_id=test_user.id,
            strava_gear_id='b55555',
            name='Bike 1'
        )
        db.session.add(bike1)
        db.session.commit()

        # Try to add another bike with the same gear_id
        bike2 = StravaBike(
            user_id=test_user.id,
            strava_gear_id='b55555',
            name='Bike 2'
        )
        db.session.add(bike2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()


