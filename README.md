**🩺 DisPred — AI-Powered Disease Prediction System**

**Disclaimer**: DisPred is an informational tool only. It does not replace professional medical advice, diagnosis, or treatment. Always consult a licensed healthcare provider for medical decisions.

**🧠 Overview**
DisPred is a full-stack, production-grade disease prediction web application that uses Deep Learning and NLP-inspired symptom matching to identify likely diseases based on user-reported symptoms.
A user selects their symptoms from a list of 377 clinically relevant symptoms, and the app runs them through a trained neural network to predict the most probable disease — along with enriched medical information like recommended medicines, prescriptions, and do's & don'ts.
The app supports user authentication, JWT-secured API calls, and prediction history, making it suitable as a real-world health informatics tool.

**✨ Key Features**
1. User Authentication:   Register & login with hashed passwords (bcrypt) and JWT tokens
2. Symptom Selection:  Multi-select from 377 real-world binary symptoms
3. AI Prediction:  Deep learning model trained on 80,000+ records across 752+ diseases
4. Medical Info:  Post-prediction enrichment with medicines, prescriptions, do's & don'ts
5. Prediction History:  Every saved prediction is stored per user in  PostgreSQL
6. Secure API:  All prediction and history routes are JWT-protected
7. REST API:  Full FastAPI backend with Swagger UI documentation
8. Interactive UI:  Clean Streamlit frontend with session-state based routing

**🛠 Tech Stack**
**Machine Learning**
  > Python, TensorFlow / Keras
  > Scikit-learn (preprocessing, train/test split)
  > NumPy, Pandas
**Backend**
  > FastAPI (REST API framework)
  > SQLAlchemy (ORM)
  > PostgreSQL (database)
  > python-jose (JWT token generation & validation)
  > passlib + bcrypt (password hashing)
  > Uvicorn (ASGI server)
**Frontend**
  > Streamlit (interactive web UI)

**🏗 System Architecture**
┌─────────────────────────────────────────────────────────────┐
│                     User (Browser)                          │
│                   Streamlit Frontend                        │
│    [Login/Register] ──► [Symptom Selection] ──► [Results]   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP requests (JSON + JWT)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│  /register  /login  /predict  /save-prediction  /history    │
└──────┬────────────────────────────────────┬─────────────────┘
       │                                    │
       ▼                                    ▼
┌─────────────────┐               ┌─────────────────────────┐
│  ML Model Layer │               │  PostgreSQL Database    │
│  disease_model  │               │  Users + Predictions    │
│  .h5 (Keras)    │               │  Tables                 │
└────────┬────────┘               └─────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              disease_info_final.json                        │
│  791 diseases → medicines, prescriptions, do's & don'ts     │
└─────────────────────────────────────────────────────────────┘

**🔄 Workflow — How It All Works**
1. REGISTER / LOGIN
   └─ User creates an account or logs in
   └─ Backend hashes the password (bcrypt) and stores in PostgreSQL
   └─ On login, a JWT token is issued and stored in Streamlit session state

2. SYMPTOM SELECTION
   └─ User selects symptoms from a multi-select dropdown (377 options)
   └─ Frontend encodes selection into a binary vector of length 377

3. PREDICTION REQUEST
   └─ Streamlit sends POST /predict with symptoms + JWT token
   └─ FastAPI validates the token and extracts user identity
   └─ The symptom vector is fed into the Keras model (disease_model.h5)
   └─ Model returns the predicted disease class

4. RESULT ENRICHMENT
   └─ Backend looks up the disease in disease_info_final.json
   └─ Returns: disease name, medicines, prescriptions, do's & don'ts

5. DISPLAY & SAVE
   └─ Streamlit displays the full prediction card to the user
   └─ User can click "Save Prediction" → stored in PostgreSQL

6. HISTORY
   └─ User navigates to History tab
   └─ Frontend calls GET /history with JWT token
   └─ Backend returns all past saved predictions for that user
