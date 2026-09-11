"""
Frontend — pure client, calls the FastAPI backend over HTTP. No ML logic here.
"""
import streamlit as st
import requests
import pandas as pd

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="UPI Fraud Detection", page_icon="🔍", layout="wide")
st.title("🔍 UPI Fraud Detection — Live Dashboard")
st.caption(f"Frontend calling live API at: `{API_URL}`")

try:
    health = requests.get(f"{API_URL}/health", timeout=5).json()
    st.success(f"✅ Backend connected — models loaded: {health['models_loaded']}")
except Exception as e:
    st.error(f"❌ Cannot reach backend API at {API_URL}. ({e})")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🔴 Live Transaction Check", "📊 Stats", "🧾 Recent Logs"])

with tab1:
    st.subheader("Send a transaction to the live model")
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.text_input("User ID", "user_0142")
        amount = st.number_input("Amount (₹)", min_value=1.0, value=500.0)
        user_avg = st.number_input("User's historical average amount (₹)", min_value=1.0, value=500.0)
    with col2:
        hour = st.slider("Hour of day", 0, 23, 14)
        day_of_week = st.selectbox("Day of week", options=list(range(7)),
                                    format_func=lambda x: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][x])
        seconds_since_last = st.number_input("Seconds since user's last transaction", min_value=0.0, value=3600.0)

    if st.button("🔎 Score this transaction via live API", type="primary"):
        payload = {
            "user_id": user_id, "amount": amount, "hour": hour,
            "day_of_week": day_of_week, "user_avg_amount": user_avg,
            "seconds_since_last_txn": seconds_since_last,
        }
        with st.spinner("Calling backend API..."):
            resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10).json()

        if resp["is_flagged"]:
            st.error(f"🚨 FRAUD ALERT — Risk: {resp['risk_level']} | Probability: {resp['fraud_probability']*100:.2f}%")
        else:
            st.success(f"✅ Approved — Risk: {resp['risk_level']} | Probability: {resp['fraud_probability']*100:.2f}%")
        st.json(resp)

    st.divider()
    st.caption("Try these presets:")
    c1, c2 = st.columns(2)
    c1.info("**Normal:** Amount ₹450, Avg ₹500, Hour 14, Gap 3600s")
    c2.warning("**Suspicious:** Amount ₹9800, Avg ₹500, Hour 2, Gap 6s")

with tab2:
    stats = requests.get(f"{API_URL}/stats", timeout=5).json()
    c1, c2 = st.columns(2)
    c1.metric("Total Transactions Scored (live)", stats["total_scored"])
    c2.metric("Total Flagged", stats["total_flagged"])

with tab3:
    logs = requests.get(f"{API_URL}/logs?limit=50", timeout=5).json()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.info("No transactions scored yet — try Tab 1.")

st.divider()
st.caption("Model: XGBoost (primary) + Isolation Forest (backup) · Built by Anurag Upadhyay")
