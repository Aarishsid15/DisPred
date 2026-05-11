from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from tensorflow import keras
import numpy as np
import joblib
import json
import os
from . database import engine, get_db, Base
from . import models
from . import schemas
from . import auth

#Create database tables
Base.metadata.create_all(bind=engine)


model = keras.models.load_model("dp_backend/DisPred_model.keras")
le_disease = joblib.load("dp_backend/le_disease.pkl")

with open("dp_backend/disease.json", "r") as f:
    disease_info = json.load(f)

# Load symptom columns
import pandas as pd
# We need symptom columns for prediction
# Load a small sample to get column names
symptom_columns = list(le_disease.classes_)  # placeholder
# Better approach — save columns during training
try:
    symptom_columns = joblib.load("dp_backend/symptom_columns.pkl")
    print(f"✅ Symptom columns loaded: {len(symptom_columns)} symptoms")
except:
    print("⚠️ symptom_columns.pkl not found — save it from Colab!")

# ── FastAPI app ───────────────────────────────────
app = FastAPI(
    title="DisPred API",
    description="Disease Prediction API",
    version="1.0.0"
)

# CORS — allows Streamlit to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper: prediction function ───────────────────
def predict_disease(symptoms_list):
    input_vector = np.zeros(len(symptom_columns))

    for symptom in symptoms_list:
        symptom = symptom.lower().strip()
        if symptom in symptom_columns:
            idx = symptom_columns.index(symptom)
            input_vector[idx] = 1

    input_vector = input_vector.reshape(1, -1)
    predictions  = model.predict(input_vector, verbose=0)

    top3_indices = np.argsort(predictions[0])[::-1][:3]
    top3_results = []
    for idx in top3_indices:
        disease_name = le_disease.inverse_transform([idx])[0]
        confidence   = round(float(predictions[0][idx]) * 100, 2)
        top3_results.append({
            "disease"    : disease_name,
            "confidence" : confidence
        })

    top_disease = top3_results[0]["disease"].lower().strip()
    info = disease_info.get(top_disease, None)

    if info:
        medicines    = info["medicines"]
        prescription = info["prescription"]
    else:
        medicines    = ["Please consult a doctor"]
        prescription = {
            "do"   : ["Consult a healthcare professional"],
            "dont" : ["Do not self-medicate"]
        }

    return {
        "top_prediction"    : top_disease,
        "confidence"        : top3_results[0]["confidence"],
        "top_3_predictions" : top3_results,
        "medicines"         : medicines,
        "prescription"      : prescription
    }


# ── Routes ────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Welcome to DisPred API!", "status": "running"}


# Register
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    # Check if username exists
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Check if email exists
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    new_user = models.User(
        username        = user.username,
        email           = user.email,
        hashed_password = auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Login
@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    # Verify user and password
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Create JWT token
    access_token = auth.create_access_token(
        data={"sub": db_user.username},
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token" : access_token,
        "token_type"   : "bearer"
    }


# Predict disease
@app.post("/predict", response_model=schemas.PredictionResponse)
def predict(
    request : schemas.PredictionRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    if not request.symptoms:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one symptom"
        )

    result = predict_disease(request.symptoms)
    return result


# Save prediction
@app.post("/save-prediction")
def save_prediction(
    request      : schemas.SavePredictionRequest,
    db           : Session = Depends(get_db),
    current_user : models.User = Depends(auth.get_current_user)
):
    import json as json_lib

    new_prediction = models.Prediction(
        user_id           = current_user.id,
        symptoms          = ", ".join(request.symptoms),
        predicted_disease = request.predicted_disease,
        confidence        = request.confidence,
        medicines         = json_lib.dumps(request.medicines),
        prescription_do   = json_lib.dumps(request.prescription_do),
        prescription_dont = json_lib.dumps(request.prescription_dont)
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {"message": "Prediction saved successfully!", "id": new_prediction.id}


# Get prediction history
@app.get("/history", response_model=list[schemas.SavedPredictionResponse])
def get_history(
    db           : Session = Depends(get_db),
    current_user : models.User = Depends(auth.get_current_user)
):
    predictions = db.query(models.Prediction).filter(
        models.Prediction.user_id == current_user.id
    ).order_by(models.Prediction.created_at.desc()).all()

    return predictions


# Get current user info
@app.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
