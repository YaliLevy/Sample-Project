"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False} if 'sqlite' in settings.DATABASE_URL else {}
)

# Enable WAL mode for SQLite for better concurrency
if 'sqlite' in settings.DATABASE_URL:
    try:
        with engine.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            logger.info("Enabled WAL mode for SQLite")
    except Exception as e:
        logger.warning(f"Could not enable WAL mode: {e}")

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


@contextmanager
def get_session() -> Session:
    """
    Context manager for database sessions.

    Usage:
        with get_session() as session:
            # Do database operations
            session.add(obj)
            # Automatically commits on success, rolls back on error
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}", exc_info=True)
        raise
    finally:
        session.close()


def get_db() -> Session:
    """
    Get a database session (for dependency injection).

    Usage:
        session = get_db()
        try:
            # Do database operations
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    """
    return SessionLocal()
