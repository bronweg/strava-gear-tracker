from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for storing Strava user information."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(100))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    profile_picture = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='owner', lazy=True, cascade='all, delete-orphan')
    strava_token = db.relationship('StravaToken', backref='user', uselist=False, cascade='all, delete-orphan')
    bikes = db.relationship('StravaBike', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Equipment(db.Model):
    """Equipment model for storing bicycle equipment information."""

    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    equipment_type = db.Column(db.String(100))  # e.g., 'Chain', 'Tires', 'Cassette', etc.
    installation_date = db.Column(db.Date, nullable=False)
    strava_bike_id = db.Column(db.String(100), nullable=True)  # Strava gear ID (optional)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to StravaBike
    bike = db.relationship('StravaBike', foreign_keys=[strava_bike_id],
                          primaryjoin='Equipment.strava_bike_id==StravaBike.strava_gear_id',
                          uselist=False, viewonly=True)
    
    def __repr__(self):
        return f'<Equipment {self.name}>'
    
    def days_since_installation(self):
        """Calculate days since installation."""
        delta = datetime.now().date() - self.installation_date
        return delta.days


class StravaToken(db.Model):
    """Model for storing Strava OAuth tokens."""

    __tablename__ = 'strava_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    access_token = db.Column(db.String(500), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StravaToken for user_id={self.user_id}>'

    def is_expired(self):
        """Check if the access token is expired."""
        return datetime.utcnow().timestamp() >= self.expires_at


class StravaBike(db.Model):
    """Model for storing Strava bikes/gear information."""

    __tablename__ = 'strava_bikes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    strava_gear_id = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(200))
    nickname = db.Column(db.String(200))
    brand_name = db.Column(db.String(200))
    model_name = db.Column(db.String(200))
    primary = db.Column(db.Boolean, default=False)
    distance = db.Column(db.Float)  # Total distance in meters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StravaBike {self.name or self.nickname}>'

    def display_name(self):
        """Get the best display name for the bike."""
        if self.nickname:
            return self.nickname
        if self.name:
            return self.name
        if self.brand_name and self.model_name:
            return f'{self.brand_name} {self.model_name}'
        return f'Bike {self.strava_gear_id}'

