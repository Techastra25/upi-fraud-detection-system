"""
Production API — loads the model ONCE at startup, exposes /predict any real
UPI backend could call over HTTPS, logs every decision to a database.
Run: uvicorn main:app --host 0.0.0.0 --port 8000
Docs: http://localhost:8000/docs
"""
import joblib
import json
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import database

MODEL_DIR = "../models"
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models["xgb"] = joblib.load(f"{MODEL_DIR}/xgb_model.pkl")
    ml_models["iso"] = joblib.load(f"{MODEL_DIR}/iso_model.pkl")
    with open(f"{MODEL_DIR}/feature_columns.json") as f:
        ml_models["features"] = json.load(f)
    database.init_db()
    print("Models loaded, database ready. API is live.")
    yield
    ml_models.clear()

app = FastAPI(
    title="UPI Fraud Detection API",
    description="Real-time fraud scoring service — XGBoost primary model + Isolation Forest safety net.",
    version="1.0.0",
    lifespan=lifespan,
)

class Transaction(BaseModel):
    user_id: str = Field(..., example="user_0142")
    amount: float = Field(..., gt=0, example=4500.0)
    hour: int = Field(..., ge=0, le=23, example=2)
    day_of_week: int = Field(..., ge=0, le=6, example=3)
    user_avg_amount: float = Field(..., gt=0, example=500.0, description="This user's historical average transaction amount")
    seconds_since_last_txn: float = Field(..., ge=0, example=8.0)

class PredictionResponse(BaseModel):
    is_flagged: bool
    fraud_probability: float
    risk_level: str
    model_used: str
    flagged_by_backup_model: bool

@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": "xgb" in ml_models}

@app.post("/predict", response_model=PredictionResponse)
def predict(txn: Transaction):
    features = ml_models["features"]
    row = {
        "amount": txn.amount, "hour": txn.hour, "day_of_week": txn.day_of_week,
        "amount_to_avg_ratio": txn.amount / txn.user_avg_amount,
        "seconds_since_last_txn": txn.seconds_since_last_txn,
        "is_odd_hour": 1 if txn.hour in [0, 1, 2, 3, 4] else 0,
    }
    X = pd.DataFrame([row])[features]

    fraud_prob = float(ml_models["xgb"].predict_proba(X)[0, 1])
    is_flagged = fraud_prob >= 0.5

    iso_score = ml_models["iso"].predict(X[["amount", "hour"]])[0]
    flagged_by_backup = iso_score == -1

    if fraud_prob >= 0.8 or flagged_by_backup:
        risk_level = "HIGH"
    elif fraud_prob >= 0.5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    final_flag = is_flagged or flagged_by_backup

    database.log_transaction(
        user_id=txn.user_id, amount=txn.amount, hour=txn.hour,
        is_flagged=int(final_flag), fraud_probability=round(fraud_prob, 4),
        model_used="xgboost+isolation_forest",
    )

    return PredictionResponse(
        is_flagged=final_flag, fraud_probability=round(fraud_prob, 4),
        risk_level=risk_level, model_used="xgboost+isolation_forest",
        flagged_by_backup_model=flagged_by_backup,
    )

@app.get("/logs")
def logs(limit: int = 50):
    return database.get_recent_logs(limit)

@app.get("/stats")
def stats():
    return database.get_stats()
