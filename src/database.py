from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sys
import os

# Ensure the root directory is in the path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

# Create SQLAlchemy engine
# connect_args={"check_same_thread": False} is required for SQLite in multithreaded Streamlit apps
if config.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(config.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

def get_db():
    """
    Database session generator context manager.
    Yields a session and automatically closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Create all tables in the database if they don't already exist.
    """
    # Import models here to register them with Base metadata
    import src.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
