from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:monty11@localhost:5432/dispred"
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:monty11@db:5432/dispred")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency — get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()