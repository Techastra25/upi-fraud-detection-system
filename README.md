# 🔍 UPI Fraud Detection System

**Real-time fraud detection service** — a decoupled backend API + live frontend dashboard, built the way an actual fintech risk team would ship it.

🔴 **Live Demo:** [Click here](https://zw5sb5ouxj.streamlit.app) &nbsp;|&nbsp; 📄 **API Docs:** [Click here](https://upi-fraud-api-7o82.onrender.com/docs)

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688) ![XGBoost](https://img.shields.io/badge/XGBoost-Model-EB6E37) ![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B) ![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)

---

## 📌 Problem Statement

India processes **15+ billion UPI transactions every month** (NPCI, 2026), and digital payment fraud — fake links, phishing, rapid-fire scam transfers — grows in direct proportion. This project builds a real-time fraud scoring service around that problem: not a notebook with a confusion matrix, but a trained model sitting behind a live API, called by a separate client, with every decision logged for audit.

## 🎯 Why This Project Is Different

Most "fraud detection" portfolio repos put everything — data, model, "API" — inside one Jupyter cell or one Streamlit script. That's a data science exercise, not an engineering one. This project separates concerns the way a real company would:

- **Model training happens once, offline**, and produces a versioned artifact (`.pkl` file)
- **The API only loads that artifact and serves predictions** — it never retrains on request
- **The frontend contains zero fraud-detection logic** — it's a pure client calling the API over HTTP, exactly like a bank's mobile app would call a payments backend
- **Every prediction is logged** to a database, because in real fraud systems an unexplainable decision is a compliance liability

## 🧠 Vision

Build a lightweight, explainable, *actually deployable* fraud detection service that a small fintech team could realistically ship — no heavy infra, no black-box deep learning, just solid feature engineering + a supervised model reasoned about the way a risk analyst thinks:
> "Is this amount unusual for **this specific user**, at **this hour**, compared to **how fast they usually transact**?"

## 🏗️ System Architecture
                ┌───────────────────────────┐
                │   Streamlit Frontend        │
                │  (pure client, no ML logic) │
                └──────────────┬────────────┘
                               │ HTTPS POST /predict
                               ▼
                ┌───────────────────────────┐
                │      FastAPI Backend        │
                │  loads model ONCE at startup │
                └──────────────┬────────────┘
                   ┌───────────┼────────────┐
                   ▼                        ▼
        ┌────────────────┐        ┌────────────────────┐
        │ XGBoost (primary)│      │ Isolation Forest      │
        │ supervised model │      │ unsupervised backup   │
        │ 98% precision    │      │ catches NEW fraud     │
        │ 100% recall       │      │ patterns not seen     │
        └────────────────┘        │ during training       │
                   │              └────────────────────┘
                   ▼
        ┌────────────────────┐
        │  SQLite Audit Log   │
        │ every decision saved │
        └────────────────────┘
        
## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Model | XGBoost (primary) + Isolation Forest (backup) | Supervised model for known fraud patterns, unsupervised safety net for unknown ones |
| Backend | FastAPI | Auto-documented, async, industry-standard for ML serving |
| Database | SQLite | Lightweight audit trail — every scored transaction is logged |
| Frontend | Streamlit | Fast, genuinely interactive dashboard, calls backend over HTTP |
| Containerization | Docker + docker-compose | Reproducible, one-command local spin-up, cloud-deployable |
| Deployment | Render (API) + Streamlit Community Cloud (frontend) | Free, real public URLs, no server management |

## ⚙️ How It Works — End to End

1. **Data generation** — 15,000 synthetic-but-realistic UPI transactions across 500 users, with three injected fraud patterns (odd-hour spikes, sudden amount spikes, rapid-fire bursts) and engineered features like `amount_to_avg_ratio` (how unusual this amount is for this specific user) and `seconds_since_last_txn` (catches rapid-fire scam bursts)
2. **Model training** (offline, once) — XGBoost trained on an 80/20 stratified split, class imbalance handled via `scale_pos_weight`; Isolation Forest trained separately as an unsupervised backup; both saved as `.pkl` artifacts
3. **API startup** — FastAPI loads both model files into memory exactly once — the single biggest difference between a demo script and a production service
4. **Live prediction** — a transaction hits `POST /predict` → features engineered on the fly → XGBoost gives a fraud probability → Isolation Forest double-checks for anomalies XGBoost wasn't trained to catch → combined risk level (`LOW`/`MEDIUM`/`HIGH`) returned in milliseconds → decision logged to SQLite
5. **Dashboard** — the Streamlit frontend calls this same live API, shows real-time stats (`/stats`), an audit log (`/logs`), and a form to test transactions interactively

## 📊 Results

| Metric (fraud class) | Score |
|---|---|
| Precision | 98.2% |
| Recall | 100% |
| F1-score | 99.1% |
| Overall accuracy | 99.9% |
| **ROC-AUC** | **0.9998** |

- Test set: 3,000 held-out transactions, stratified split, never seen during training
- **Top predictive feature: `amount_to_avg_ratio` (98.7% of the model's decision weight)** — confirming fraud detection is fundamentally about *relative*, per-user behavior, not fixed thresholds
- 15,000 transactions, 500 users, ~4% fraud rate

## 💡 Key Design Decisions (what to say when a recruiter asks "walk me through this")

- **Why XGBoost over Isolation Forest as the primary model?** Once labeled fraud data exists, supervised learning directly learns what fraud looks like instead of just flagging "statistically unusual" — that's why it hits 98%+ precision.
- **Why keep Isolation Forest at all?** XGBoost can only catch fraud patterns it was trained on. A brand-new scam technique won't have a label yet — Isolation Forest is the safety net for exactly that blind spot, mirroring how real fraud stacks are built.
- **Why load the model once at API startup instead of per-request?** A payment decision has to happen in milliseconds. Reloading a model from disk on every request would make that impossible.
- **Why separate the frontend from the backend at all?** In the real world, the client calling this API might be a bank's mobile app, not a Streamlit page — the API has to work independent of how it's visualized.
- **Precision vs recall trade-off:** A missed fraud (false negative) costs real money; an over-flagged normal transaction (false positive) annoys a real user. This model is tuned to keep recall at 100% — catching every fraud case in testing — while keeping precision high enough that a review team wouldn't be flooded with false alarms.

## 💰 Business Impact

- At 100% recall on this test set, **zero fraudulent transactions slip through undetected**
- At 98%+ precision, **fewer than 2 in 100 flagged transactions are false alarms** — low enough noise that a real ops team could review flags manually without alert fatigue
- Sub-100ms scoring means this could sit **in the critical path of a real payment**, blocking fraud before money moves — not just reporting it afterward in a batch report

## 🚀 Run It Yourself

**Option A — Docker (recommended, one command):**
```bash
git clone https://github.com/<your-username>/upi-fraud-detection-system.git
cd upi-fraud-detection-system
docker-compose up --build
```
API → `http://localhost:8000/docs` &nbsp;|&nbsp; Frontend → `http://localhost:8501`

**Option B — Manual:**
```bash
pip install -r requirements.txt
cd data_generation && python3 generate_data.py
cd ../training && python3 train_model.py
cd ../api && uvicorn main:app --reload --port 8000
# in a second terminal:
cd frontend && streamlit run app.py
```

## 🌍 Get a Real Live Link (2 free deploys, ~10 minutes, no coding)

**1) Deploy the backend on Render.com (free):**
- Sign up at render.com with your GitHub account
- Click "New +" → "Web Service" → select your `upi-fraud-detection-system` repo
- Render auto-detects the `Dockerfile` → click "Create Web Service"
- Wait ~3 minutes → you get a URL like `https://upi-fraud-api.onrender.com`
- Check it worked: open `https://upi-fraud-api.onrender.com/docs` in your browser

**2) Deploy the frontend on Streamlit Community Cloud (free):**
- Sign in at share.streamlit.io with your GitHub account
- Click "New app" → select your repo → set main file path to `frontend/app.py`
- Click "Advanced settings" → "Secrets" → paste this (replace with your real Render URL from step 1):
- - Click "Deploy" → you get a URL like `https://upi-fraud-detection.streamlit.app`

**That second link is what you share with recruiters.** Paste it at the top of this README and on your resume/LinkedIn.

## 🔮 Future Scope

- [ ] Validate against a real public fraud dataset (e.g. Kaggle Credit Card Fraud) alongside this synthetic one, to compare performance on real-world data
- [ ] Add SHAP explainability so every flagged transaction shows *exactly why* it was flagged
- [ ] Add model monitoring — track precision/recall drift over time, trigger automatic retraining
- [ ] Move SQLite → PostgreSQL for a multi-instance production setup
- [ ] Add authentication (API keys/JWT) on the `/predict` endpoint
- [ ] Deploy on Kubernetes with autoscaling for real transaction-volume load testing

## 📁 Project Structure
upi-fraud-detection-system/
├── data_generation/generate_data.py # synthetic data with engineered features
├── training/train_model.py # trains + saves XGBoost & Isolation Forest
├── api/main.py # FastAPI backend — the real service
├── api/database.py # SQLite audit logging
├── frontend/app.py # Streamlit client, calls the API
├── models/ # saved model artifacts (.pkl, already trained)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

## 🧑‍💻 About This Project

Built to demonstrate the full engineering lifecycle around a machine learning system: data → training → a real served API → a real client → deployment — not just a notebook with a metrics table. Happy to walk through any design decision in an interview.

**Author:** Anurag Upadhyay
**LinkedIn:** [linkedin.com/in/anurag-upadhyay-49b4b4362](https://www.linkedin.com/in/anurag-upadhyay-49b4b4362)

