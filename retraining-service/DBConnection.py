from sqlmodel import create_engine, Session, text
from Settings import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,
    max_overflow=10
)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session


def test_connection():
    """Test database connection"""
    try:
        logger.info(f"Testing database connection... {settings.DATABASE_URL}")
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False