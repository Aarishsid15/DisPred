from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . database import Base

# Users table
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, unique=True, index=True, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    # Relationship — one user has many predictions
    predictions   = relationship("Prediction", back_populates="owner")


# Predictions table
class Prediction(Base):
    __tablename__ = "predictions"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptoms        = Column(Text, nullable=False)      # stored as comma separated
    predicted_disease = Column(String, nullable=False)
    confidence      = Column(Float, nullable=False)
    medicines       = Column(Text, nullable=False)      # stored as JSON string
    prescription_do   = Column(Text, nullable=False)    # stored as JSON string
    prescription_dont = Column(Text, nullable=False)    # stored as JSON string
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Relationship — prediction belongs to user
    owner           = relationship("User", back_populates="predictions")