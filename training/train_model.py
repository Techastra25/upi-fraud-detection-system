"""
STEP 2: Train XGBoost (primary, supervised) + Isolation Forest (backup, unsupervised)
and save both as artifacts. Self-contained, no external data needed.
"""
import pandas as pd
import numpy as np
import joblib
import json
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../upi_transactions.csv", parse_dates=["timestamp"])

FEATURES = ["amount", "hour", "day_of_week", "amount_to_avg_ratio",
            "seconds_since_last_txn", "is_odd_hour"]
X = df[FEATURES]
y = df["is_fraud"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

xgb_model = XGBClassifier(
    n_estimators=200, max_depth=4, learning_rate=0.1,
    scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
    eval_metric="logloss", random_state=42,
)
xgb_model.fit(X_train, y_train)

preds = xgb_model.predict(X_test)
probs = xgb_model.predict_proba(X_test)[:, 1]

print("=== XGBoost (Supervised) — Test Set Performance ===")
print(confusion_matrix(y_test, preds))
print(classification_report(y_test, preds, digits=3))
print(f"ROC-AUC: {roc_auc_score(y_test, probs):.4f}")

iso_model = IsolationForest(contamination=0.03, random_state=42)
iso_model.fit(X_train[["amount", "hour"]])

joblib.dump(xgb_model, "../models/xgb_model.pkl")
joblib.dump(iso_model, "../models/iso_model.pkl")
with open("../models/feature_columns.json", "w") as f:
    json.dump(FEATURES, f)

feature_importance = dict(zip(FEATURES, xgb_model.feature_importances_.round(4).tolist()))
print("\nFeature importances:", feature_importance)
print("\nSaved -> models/xgb_model.pkl, models/iso_model.pkl")
