from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/clinical_copilot"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

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