from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable. Defaults to a local SQLite file so
# the backend runs out of the box for local development; Docker Compose overrides
# this with a PostgreSQL URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# SQLite needs a special connect arg when used with FastAPI's threaded workers.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 