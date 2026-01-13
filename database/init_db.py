"""
Database initialization script.
Creates tables and optionally seeds test data.
"""
import os
import logging
from database.models import Base, Property, Client, Photo, Match, Conversation
from database.connection import engine, get_session
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def seed_test_data():
    """Seed database with Hebrew test data for development."""
    logger.info("Seeding test data...")

    with get_session() as session:
        # Check if data already exists
        existing_properties = session.query(Property).count()
        if existing_properties > 0:
            logger.info("Database already contains data, skipping seed")
            return

        # Add test properties
        properties = [
            Property(
                property_type="דירה",
                city="תל אביב",
                street="דיזנגוף",
                street_number="102",
                address="דיזנגוף 102, תל אביב",
                rooms=3,
                size=75,
                floor=2,
                price=5000,
                transaction_type="rent",
                owner_name="יוסי כהן",
                owner_phone="0534439430",
                description="דירה משופצת וממוזגת, קרובה לים",
                status="available",
                phone_number="+972501234567"
            ),
            Property(
                property_type="בית",
                city="רעננה",
                street="הרצל",
                street_number="25",
                address="הרצל 25, רעננה",
                rooms=5,
                size=150,
                price=4000000,
                transaction_type="sale",
                owner_name="דינה לוי",
                owner_phone="0521234567",
                description="בית פרטי עם גינה גדולה, מחסן וחניה",
                status="available",
                phone_number="+972501234567"
            ),
            Property(
                property_type="דירה",
                city="ירושלים",
                street="יפו",
                street_number="150",
                address="יפו 150, ירושלים",
                rooms=2,
                size=55,
                floor=1,
                price=4000,
                transaction_type="rent",
                owner_name="משה אברהם",
                owner_phone="0546789012",
                description="דירה קטנה וחמודה, כולל ארנונה",
                status="available",
                phone_number="+972501234567"
            ),
            Property(
                property_type="דירה",
                city="חיפה",
                street="הרצל",
                street_number="88",
                address="הרצל 88, חיפה",
                rooms=4,
                size=95,
                floor=3,
                price=6500,
                transaction_type="rent",
                owner_name="רחל גולן",
                owner_phone="0523456789",
                description="דירה מרווחת עם מרפסת גדולה ונוף לים",
                status="available",
                phone_number="+972501234567"
            ),
        ]

        session.add_all(properties)
        session.flush()  # Get IDs for properties

        # Add test clients
        clients = [
            Client(
                name="יניב כהן",
                phone="0501112233",
                looking_for="rent",
                property_type="דירה",
                city="תל אביב",
                min_rooms=2,
                max_rooms=3,
                min_price=4000,
                max_price=6000,
                preferred_areas='["דיזנגוף", "בן יהודה", "אבן גבירול"]',
                status="active",
                phone_number="+972501234567"
            ),
            Client(
                name="דני לוי",
                phone="0502223344",
                looking_for="rent",
                property_type="דירה",
                city="תל אביב",
                min_rooms=3,
                max_rooms=4,
                min_price=5000,
                max_price=7000,
                min_size=70,
                preferred_areas='["צפון תל אביב", "רמת אביב"]',
                status="active",
                phone_number="+972501234567"
            ),
            Client(
                name="שרה מזרחי",
                phone="0503334455",
                looking_for="buy",
                property_type="בית",
                city="רעננה",
                min_rooms=4,
                max_rooms=6,
                min_price=3000000,
                max_price=5000000,
                min_size=120,
                notes="מחפשת בית עם גינה לילדים",
                status="active",
                phone_number="+972501234567"
            ),
        ]

        session.add_all(clients)
        session.flush()

        # Create some matches
        # יניב כהן matches property 1 (דיזנגוף)
        match1 = Match(
            property_id=properties[0].id,
            client_id=clients[0].id,
            score=95.0,
            status="suggested"
        )

        # דני לוי matches property 1 (דיזנגוף)
        match2 = Match(
            property_id=properties[0].id,
            client_id=clients[1].id,
            score=85.0,
            status="suggested"
        )

        # שרה מזרחי matches property 2 (house in רעננה)
        match3 = Match(
            property_id=properties[1].id,
            client_id=clients[2].id,
            score=90.0,
            status="suggested"
        )

        session.add_all([match1, match2, match3])

        logger.info(f"Seeded {len(properties)} properties, {len(clients)} clients, and 3 matches")


def drop_tables():
    """Drop all database tables (use with caution!)."""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(engine)
    logger.info("All tables dropped")


def reset_database():
    """Drop and recreate all tables."""
    drop_tables()
    create_tables()
    seed_test_data()


def init_database(seed=False):
    """
    Initialize database: create tables and optionally seed test data.

    Args:
        seed: Whether to seed test data (default: False)
    """
    logger.info(f"Initializing database at: {settings.DATABASE_URL}")

    # Ensure storage directory exists
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

    # Create tables
    create_tables()

    # Optionally seed test data
    if seed:
        seed_test_data()

    logger.info("Database initialization complete")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_database()
    elif len(sys.argv) > 1 and sys.argv[1] == 'seed':
        seed_test_data()
    else:
        # Default: just create tables
        init_database(seed=True)
