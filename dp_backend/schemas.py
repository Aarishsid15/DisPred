from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ── Auth schemas ──────────────────────────────────

class UserRegister(BaseModel):
    username  : str
    email     : EmailStr
    password  : str

class UserLogin(BaseModel):
    username  : str
    password  : str

class UserResponse(BaseModel):
    id         : int
    username   : str
    email      : str
    created_at : datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token : str
    token_type   : str

class TokenData(BaseModel):
    username : Optional[str] = None


# ── Prediction schemas ────────────────────────────

class PredictionRequest(BaseModel):
    symptoms : List[str]   # e.g. ["fever", "cough", "fatigue"]

class PredictionResponse(BaseModel):
    top_prediction    : str
    confidence        : float
    top_3_predictions : List[dict]
    medicines         : List[str]
    prescription      : dict

class SavePredictionRequest(BaseModel):
    symptoms          : List[str]
    predicted_disease : str
    confidence        : float
    medicines         : List[str]
    prescription_do   : List[str]
    prescription_dont : List[str]

class SavedPredictionResponse(BaseModel):
    id                : int
    symptoms          : str
    predicted_disease : str
    confidence        : float
    created_at        : datetime
    medicines         : str
    prescription_do   : str
    prescription_dont : str

    class Config:
        from_attributes = True