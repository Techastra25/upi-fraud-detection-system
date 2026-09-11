# 🔍 UPI Fraud Detection System

**Real-time fraud detection service** — a decoupled backend API + live frontend dashboard, built the way an actual fintech risk team would ship it.

🔴 **Live Demo:** _[add link after deploying — steps below]_ &nbsp;|&nbsp; 📄 **API Docs:** _[add link after deploying]_

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
