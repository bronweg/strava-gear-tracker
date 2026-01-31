from datetime import datetime
from models import db, Equipment, StravaBike
from strava_service import StravaService


class EquipmentService:
    """Service for managing equipment CRUD operations."""
    
    @staticmethod
    def create_equipment(user, name, equipment_type, installation_date, notes=None, strava_bike_id=None):
        """
        Create a new equipment item.

        Args:
            user: User object
            name: Equipment name
            equipment_type: Type of equipment
            installation_date: Date when equipment was installed (datetime.date)
            notes: Optional notes
            strava_bike_id: Optional Strava gear ID to associate with specific bike

        Returns:
            Equipment object
        """
        equipment = Equipment(
            user_id=user.id,
            name=name,
            equipment_type=equipment_type,
            installation_date=installation_date,
            strava_bike_id=strava_bike_id,
            notes=notes
        )

        db.session.add(equipment)
        db.session.commit()

        return equipment
    
    @staticmethod
    def get_equipment_by_id(equipment_id, user):
        """Get equipment by ID, ensuring it belongs to the user."""
        return Equipment.query.filter_by(id=equipment_id, user_id=user.id).first()
    
    @staticmethod
    def get_all_equipment(user):
        """Get all equipment for a user."""
        return Equipment.query.filter_by(user_id=user.id).order_by(Equipment.installation_date.desc()).all()
    
    @staticmethod
    def update_equipment(equipment_id, user, name=None, equipment_type=None,
                        installation_date=None, notes=None, strava_bike_id=None):
        """
        Update an equipment item.

        Args:
            equipment_id: ID of equipment to update
            user: User object
            name: New name (optional)
            equipment_type: New type (optional)
            installation_date: New installation date (optional)
            notes: New notes (optional)
            strava_bike_id: New Strava bike ID (optional, use empty string to clear)

        Returns:
            Updated Equipment object or None if not found
        """
        equipment = EquipmentService.get_equipment_by_id(equipment_id, user)

        if not equipment:
            return None

        if name is not None:
            equipment.name = name
        if equipment_type is not None:
            equipment.equipment_type = equipment_type
        if installation_date is not None:
            equipment.installation_date = installation_date
        if notes is not None:
            equipment.notes = notes
        if strava_bike_id is not None:
            # Allow empty string to clear the bike association
            equipment.strava_bike_id = strava_bike_id if strava_bike_id else None

        equipment.updated_at = datetime.utcnow()
        db.session.commit()

        return equipment
    
    @staticmethod
    def delete_equipment(equipment_id, user):
        """
        Delete an equipment item.
        
        Args:
            equipment_id: ID of equipment to delete
            user: User object
        
        Returns:
            True if deleted, False if not found
        """
        equipment = EquipmentService.get_equipment_by_id(equipment_id, user)
        
        if not equipment:
            return False
        
        db.session.delete(equipment)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_equipment_with_stats(user):
        """
        Get all equipment with calculated Strava statistics.

        Returns:
            List of dictionaries with equipment and stats
        """
        equipment_list = EquipmentService.get_all_equipment(user)
        strava_service = StravaService(user)

        result = []

        for equipment in equipment_list:
            try:
                # Use bike-specific stats calculation if bike is associated
                stats = strava_service.calculate_equipment_stats_for_bike(
                    equipment.installation_date,
                    equipment.strava_bike_id
                )

                result.append({
                    'equipment': equipment,
                    'stats': stats
                })
            except Exception as e:
                # If there's an error fetching stats, still include the equipment
                result.append({
                    'equipment': equipment,
                    'stats': {
                        'total_distance_km': 0,
                        'total_time_hours': 0,
                        'days_elapsed': equipment.days_since_installation(),
                        'activity_count': 0,
                        'error': str(e)
                    }
                })

        return result

    @staticmethod
    def sync_bikes_from_strava(user):
        """
        Sync bikes from Strava API to local database.

        Args:
            user: User object

        Returns:
            Number of bikes synced
        """
        strava_service = StravaService(user)

        try:
            bikes_data = strava_service.get_athlete_bikes()

            for bike_data in bikes_data:
                # Check if bike already exists
                existing_bike = StravaBike.query.filter_by(
                    strava_gear_id=bike_data['id']
                ).first()

                if existing_bike:
                    # Update existing bike
                    existing_bike.name = bike_data.get('name')
                    existing_bike.nickname = bike_data.get('nickname')
                    existing_bike.brand_name = bike_data.get('brand_name')
                    existing_bike.model_name = bike_data.get('model_name')
                    existing_bike.primary = bike_data.get('primary', False)
                    existing_bike.distance = bike_data.get('distance', 0)
                    existing_bike.updated_at = datetime.utcnow()
                else:
                    # Create new bike
                    new_bike = StravaBike(
                        user_id=user.id,
                        strava_gear_id=bike_data['id'],
                        name=bike_data.get('name'),
                        nickname=bike_data.get('nickname'),
                        brand_name=bike_data.get('brand_name'),
                        model_name=bike_data.get('model_name'),
                        primary=bike_data.get('primary', False),
                        distance=bike_data.get('distance', 0)
                    )
                    db.session.add(new_bike)

            db.session.commit()
            return len(bikes_data)

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_bikes(user):
        """
        Get all bikes for a user from the database.

        Args:
            user: User object

        Returns:
            List of StravaBike objects
        """
        return StravaBike.query.filter_by(user_id=user.id).order_by(StravaBike.primary.desc()).all()

