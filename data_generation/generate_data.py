"""
STEP 1: Generate synthetic UPI transactions with realistic behavioral features.
Fully self-contained -- no external downloads needed, runs anywhere in seconds.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N_USERS = 500
N_TXNS = 15000
FRAUD_RATE = 0.04

banks = ["SBI", "HDFC", "ICICI", "Axis", "PNB", "Kotak", "BOB", "Paytm"]
user_ids = [f"user_{i:04d}" for i in range(N_USERS)]
user_profile = {u: {"mean": np.random.uniform(150, 3000), "std": np.random.uniform(50, 500)} for u in user_ids}

start_date = datetime(2026, 1, 1)
rows = []

for i in range(N_TXNS):
    user = random.choice(user_ids)
    profile = user_profile[user]
    is_fraud = np.random.rand() < FRAUD_RATE

    ts = start_date + timedelta(days=random.randint(0, 240), hours=random.randint(0, 23),
                                 minutes=random.randint(0, 59), seconds=random.randint(0, 59))

    if not is_fraud:
        amount = max(10, np.random.normal(profile["mean"], profile["std"]))
        seconds_since_last_txn = np.random.uniform(300, 86400)
    else:
        fraud_type = random.choice(["odd_hour_spike", "amount_spike", "rapid_fire"])
        if fraud_type == "odd_hour_spike":
            ts = ts.replace(hour=random.choice([1, 2, 3, 4]))
            amount = profile["mean"] * random.uniform(8, 20)
            seconds_since_last_txn = np.random.uniform(300, 86400)
        elif fraud_type == "amount_spike":
            amount = profile["mean"] * random.uniform(10, 30)
            seconds_since_last_txn = np.random.uniform(300, 86400)
        else:
            amount = profile["mean"] * random.uniform(3, 8)
            seconds_since_last_txn = np.random.uniform(1, 30)

    rows.append({
        "transaction_id": f"TXN{i:06d}", "user_id": user, "bank": random.choice(banks),
        "amount": round(amount, 2), "timestamp": ts, "hour": ts.hour,
        "day_of_week": ts.weekday(), "user_avg_amount": round(profile["mean"], 2),
        "seconds_since_last_txn": round(seconds_since_last_txn, 1), "is_fraud": int(is_fraud),
    })

df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
df["amount_to_avg_ratio"] = df["amount"] / df["user_avg_amount"]
df["is_odd_hour"] = df["hour"].isin([0, 1, 2, 3, 4]).astype(int)

df.to_csv("../upi_transactions.csv", index=False)
print(df["is_fraud"].value_counts())
print(f"Saved {len(df)} transactions -> upi_transactions.csv")
