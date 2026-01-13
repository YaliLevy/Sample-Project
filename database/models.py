"""
SQLAlchemy ORM models for the WhatsApp Real Estate Assistant.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Property(Base):
    """
    Real estate property model.
    Supports both rental and sale properties.
    """
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Property details
    property_type = Column(String(50), nullable=False)  # דירה, בית, מגרש, etc.
    city = Column(String(100), nullable=False, default='תל אביב', index=True)
    street = Column(String(200))
    street_number = Column(String(20))
    address = Column(String(500))  # Full address string

    rooms = Column(Float, index=True)  # Can be 2.5, 3.5, etc.
    size = Column(Integer)  # Square meters
    floor = Column(Integer)
    price = Column(Integer, nullable=False, index=True)  # In ILS

    transaction_type = Column(String(20), nullable=False, index=True)  # 'rent' or 'sale'

    # Owner information
    owner_name = Column(String(200))
    owner_phone = Column(String(20))

    description = Column(Text)

    # Status tracking
    status = Column(String(20), default='available', index=True)  # available, rented, sold, pending

    # Metadata
    phone_number = Column(String(20), nullable=False)  # Who added this property
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    photos = relationship("Photo", back_populates="property", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="property", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize property to dictionary for agents."""
        return {
            'id': self.id,
            'property_type': self.property_type,
            'city': self.city,
            'street': self.street,
            'street_number': self.street_number,
            'address': self.address,
            'rooms': self.rooms,
            'size': self.size,
            'floor': self.floor,
            'price': self.price,
            'transaction_type': self.transaction_type,
            'owner_name': self.owner_name,
            'owner_phone': self.owner_phone,
            'description': self.description,
            'status': self.status,
            'photo_count': len(self.photos),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Property(id={self.id}, type={self.property_type}, city={self.city}, rooms={self.rooms}, price={self.price})>"


class Client(Base):
    """
    Client model for people looking for properties.
    """
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Client information
    name = Column(String(200), nullable=False)
    phone = Column(String(20))

    # Search criteria
    looking_for = Column(String(20), nullable=False, index=True)  # 'rent' or 'buy'
    property_type = Column(String(50))  # דירה, בית, etc.
    city = Column(String(100), index=True)  # Preferred city

    min_rooms = Column(Float)
    max_rooms = Column(Float)
    min_price = Column(Integer, index=True)
    max_price = Column(Integer, index=True)
    min_size = Column(Integer)  # Minimum square meters

    preferred_areas = Column(Text)  # JSON array of area names
    notes = Column(Text)

    # Status tracking
    status = Column(String(20), default='active', index=True)  # active, closed, pending

    # Metadata
    phone_number = Column(String(20), nullable=False)  # Who added this client
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matches = relationship("Match", back_populates="client", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize client to dictionary for agents."""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'looking_for': self.looking_for,
            'property_type': self.property_type,
            'city': self.city,
            'min_rooms': self.min_rooms,
            'max_rooms': self.max_rooms,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'min_size': self.min_size,
            'preferred_areas': self.preferred_areas,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name}, looking_for={self.looking_for}, city={self.city})>"


class Photo(Base):
    """
    Property photo model.
    Photos are downloaded from Twilio and stored locally.
    """
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, autoincrement=True)

    property_id = Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True)

    # Photo storage
    file_path = Column(String(500), nullable=False)  # Local storage path
    twilio_media_url = Column(String(500))  # Original Twilio URL for debugging
    media_content_type = Column(String(50))  # image/jpeg, image/png, etc.

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    # Relationships
    property = relationship("Property", back_populates="photos")

    def __repr__(self):
        return f"<Photo(id={self.id}, property_id={self.property_id}, path={self.file_path})>"


class Match(Base):
    """
    Property-client match model.
    Tracks suggested matches with quality scores.
    """
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, autoincrement=True)

    property_id = Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)

    score = Column(Float, nullable=False)  # Match quality 0-100

    # Status tracking
    status = Column(String(20), default='suggested', index=True)  # suggested, sent, interested, rejected, closed

    # Metadata
    suggested_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    property = relationship("Property", back_populates="matches")
    client = relationship("Client", back_populates="matches")

    def to_dict(self):
        """Serialize match to dictionary."""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'client_id': self.client_id,
            'score': self.score,
            'status': self.status,
            'suggested_at': self.suggested_at.isoformat() if self.suggested_at else None,
        }

    def __repr__(self):
        return f"<Match(id={self.id}, property_id={self.property_id}, client_id={self.client_id}, score={self.score})>"


class Conversation(Base):
    """
    Conversation history model.
    Tracks all messages for context and debugging.
    """
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)

    phone_number = Column(String(20), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, server_default=func.now(), index=True)

    def to_dict(self):
        """Serialize conversation to dictionary."""
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

    def __repr__(self):
        return f"<Conversation(id={self.id}, phone={self.phone_number}, role={self.role})>"
