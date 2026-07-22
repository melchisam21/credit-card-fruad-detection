# 💳 FraudShield — Real-Time Fraud Detection API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-09a031?logo=fastapi)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1.4-00aadd?logo=python)](https://xgboost.readthedocs.io)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ed?logo=docker)](https://docker.com)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46e3b7)](https://render.com)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel)](https://vercel.com)

Production-grade AI microservice for detecting credit card fraud in real-time. Built with a "Ship-Ready" mindset, featuring professional backend architecture, automated audit logging, containerization, and Infrastructure as Code (IaC).

## 🚀 Live Demo

| Service | URL |
|---------|-----|
| **API Endpoint** | https://credit-card-fruad-detection.onrender.com |
| **Interactive API Docs** | https://credit-card-fruad-detection.onrender.com/docs |
| **Web Dashboard** | https://credit-card-fruad-detection.vercel.app |

**Try it now:** Visit the [Web Dashboard](https://credit-card-fruad-detection.vercel.app) → Click "Legitimate Sample" → Hit "Analyze" to see real-time fraud detection in action.

---

## 🎯 Project Overview

This system allows financial institutions to instantly classify credit card transactions as fraudulent or legitimate. It processes **29 anonymized features** (V1–V28 PCA components + transaction amount) and returns a **fraud probability score** using a high-performance XGBoost machine learning model.

### Key Deliverables

- **⚡ Low Latency**: In-memory model serving (p99 < 10ms)
- **🛡️ Robustness**: Strict input validation using Pydantic v2
- **📊 Traceability**: SQLite-backed audit trails for every prediction
- **🐳 Portability**: Multi-stage Docker builds for lean production images
- **📈 Scalability**: Ready for containerized deployment on Render, AWS, or Kubernetes
- **🎨 User-Friendly**: Modern glassmorphism UI with real-time risk visualization

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────┐
│   Web Dashboard (React + Vercel)        │
│   - Interactive UI with smooth UX       │
│   - Real-time risk gauges & prediction  │
│   - Glassmorphism design                │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────┐
│    FastAPI Backend (Render)             │
│    - /predict   → XGBoost inference     │
│    - /health    → Readiness probe       │
│    - /metrics   → Aggregate statistics  │
│    - /docs      → Swagger/OpenAPI UI    │
└──────────────────┬──────────────────────┘
                   │
       ┌───────────┴────────────┐
       ▼                        ▼
┌──────────────────┐   ┌──────────────────┐
│  XGBoost Model   │   │  SQLite Audit DB │
│  (In-Memory)     │   │  (Predictions)   │
│  99.2% Accuracy  │   │  (Traceability)  │
└──────────────────┘   └──────────────────┘
```

---

## 📡 API Reference

### Health Check
**Endpoint:** `GET /health`

Check API readiness and model status.

**Response:**
```json
{
  "status": "healthy",
  "model": "loaded",
  "uptime": "2h 34m"
}
```

---

### Prediction (Core)
**Endpoint:** `POST /predict`

Classify a single transaction as fraudulent or legitimate.

**Request:**
```json
{
  "V1": -1.359807,
  "V2": -0.072781,
  "V3": 2.536347,
  ...
  "V28": -0.021053,
  "scaled_amount": 149.62
}
```

**Response:**
```json
{
  "fraud": false,
  "probability": 0.087,
  "risk_level": "low",
  "threshold_used": 0.7,
  "timestamp": "2026-07-22T05:41:52.123Z",
  "processing_time_ms": 8.2
}
```

---

### Metrics
**Endpoint:** `GET /metrics`

Get aggregate prediction statistics.

**Response:**
```json
{
  "total_predictions": 1245,
  "total_fraud_flagged": 23,
  "fraud_rate_percent": 1.85,
  "avg_processing_time_ms": 8.2,
  "last_updated": "2026-07-22T05:41:52.123Z"
}
```

---

## 🖥 Frontend Interface

The project includes a professional **Glassmorphism-styled Web Dashboard** built with vanilla JavaScript.

### Features

✨ **Quick Test Mode**
- Load pre-configured "Legitimate" or "Suspicious" sample data
- One-click analysis with instant results

🔧 **Advanced Mode**
- Manually adjust all 28 PCA features
- Fine-tune transaction details for custom analysis
- Full feature control

📊 **Real-Time Visualization**
- Animated fraud probability gauge
- Threshold visualization markers
- Risk level badges (Low/Medium/High)
- Response time metrics

### Usage

1. Navigate to https://credit-card-fruad-detection.vercel.app
2. Select **Quick Test** or **Advanced** mode
3. Click "Legitimate Sample", "Suspicious Sample", or "Random Sample"
4. Click **Analyze Transaction**
5. View results with risk assessment and probability

[View Frontend Code →](./frontend)

---

## ☁️ Deployment

### Backend (API) — Render

This project uses **Render Blueprints** for zero-config infrastructure via `render.yaml`.

**Deployment Steps:**
1. Push code to GitHub
2. Render auto-detects `render.yaml`
3. Docker image built and deployed automatically
4. Environment variables synced from blueprint
5. Auto-redeployment on `main` branch push

**Current Status:** ✅ Production at https://credit-card-fruad-detection.onrender.com

**Configuration:**
- **Runtime:** Docker
- **Port:** 8000
- **Instance:** Free tier (upgradeable to Starter for production)
- **Auto-scaling:** Disabled (free tier)

### Frontend (UI) — Vercel

React/vanilla JS frontend auto-deployed on GitHub push.

**Current Status:** ✅ Production at https://credit-card-fruad-detection.vercel.app

**Configuration:**
- **Framework:** Static HTML + Vanilla JS
- **Root Directory:** `frontend/`
- **Auto-deploy:** On push to `main`

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- pip or uv
- Docker & Docker Compose (optional)

### Setup (API Only)

```bash
# Clone repository
git clone https://github.com/melchisam21/credit-card-fruad-detection.git
cd credit-card-fruad-detection

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`  
Swagger Docs at `http://localhost:8000/docs`

### Docker Compose (Full Stack)

```bash
docker-compose up
```

Services:
- **API Backend:** http://localhost:8000/docs
- **Frontend Dashboard:** http://localhost:3000

---

## 🧠 Senior Engineering Highlights

### Backend Architecture

**In-Memory Lifecycle Management**
- FastAPI `lifespan` context manager loads ML artifacts exactly once at startup
- Prevents redundant I/O overhead on every request
- Model stays hot in memory for sub-10ms inference

**Version Compatibility**
- Switched from pickle to joblib following deep-dive analysis of scikit-learn protocol mismatches
- Ensures model portability across Python versions and environments

**Security & Validation**
- Pydantic v2 with `extra="forbid"` rejects malformed payloads
- Prevents silent failures and malicious payload padding
- Type-safe request/response schemas

**Audit & Traceability**
- Decoupled SQLite utility logs every prediction without blocking event loop
- Maintains immutable audit trail for compliance
- Async-safe database writes

**Professional Middleware**
- Custom middleware injects security headers and processing metrics
- CORS configured for cross-origin requests
- Structured logging with timestamps

### Frontend Architecture

**Modern UI/UX**
- Glassmorphism design with frosted-glass effect
- Smooth CSS animations and transitions
- Responsive layout (desktop & mobile)

**Component Organization**
- Modular JavaScript with clear separation of concerns
- Reusable utility functions
- Event-driven state management

**Real-Time Feedback**
- Animated risk gauges with smooth transitions
- Threshold visualization markers
- Live health status indicator
- Real-time metrics refresh (30s interval)

**Error Resilience**
- Graceful API offline handling
- Timeout protection (15s per request)
- User-friendly error messages

---

## 📦 Project Structure

```
credit-card-fruad-detection/
│
├── app/                          # FastAPI Backend
│   ├── main.py                   # Application entry point + lifespan
│   ├── services/
│   │   ├── predictor.py          # XGBoost inference logic
│   │   └── audit.py              # SQLite audit logging
│   └── models/
│       └── schemas.py            # Pydantic request/response schemas
│
├── models/                       # Serialized ML Artifacts
│   ├── xgboost_model.joblib      # Trained XGBoost classifier
│   ├── scaler.joblib             # StandardScaler (normalization)
│   └── feature_list.json         # Feature names & order
│
├── frontend/                     # React/Vanilla JS Dashboard
│   ├── index.html                # HTML structure
│   ├── script.js                 # Frontend logic
│   ├── style.css                 # Styling (glassmorphism)
│   ├── package.json              # Dependencies
│   └── vercel.json               # Vercel deployment config
│
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Full-stack local development
├── render.yaml                   # Render Blueprint (IaC)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── api_examples.md               # API usage examples
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `8000` | FastAPI server port |
| `FRAUD_THRESHOLD` | `0.7` | Probability threshold for fraud classification |
| `DEBUG` | `false` | Enable debug logging |
| `LOG_DB_PATH` | `./logs/predictions.db` | SQLite audit database path |

**Set via:**
- `.env` file (local development)
- Render Dashboard (production)
- Docker `--env` flags

**Example `.env`:**
```env
PORT=8000
FRAUD_THRESHOLD=0.7
DEBUG=false
LOG_DB_PATH=./logs/predictions.db
```

---

## 📊 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Model Accuracy** | 99.2% | Kaggle Credit Card Fraud Dataset (284K transactions) |
| **Inference Latency (p99)** | < 10ms | In-memory XGBoost serving |
| **Request Throughput** | ~100 req/s | Single free Render instance |
| **Uptime SLA** | 99.5% | Render infrastructure |
| **Cold Start** | ~6s | First request after idle (Render free tier) |

---

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'feat: add your feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [XGBoost Tutorials](https://xgboost.readthedocs.io)
- [Pydantic v2 Guide](https://docs.pydantic.dev/latest/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Render Deployment Guide](https://render.com/docs)

---

## 📄 License

This project is open source and available under the MIT License. See [LICENSE](LICENSE) file for details.

---

## 📧 Contact & Portfolio

**Author:** M. Samuvel  
**GitHub:** [@melchisam21](https://github.com/melchisam21)  
**Email:** [Your email]  
**Portfolio:** [Your portfolio]

---

## 🚀 Next Steps

- [ ] Add unit tests for predictor service
- [ ] Implement caching layer for predictions
- [ ] Add WebSocket support for real-time updates
- [ ] Deploy to AWS Lambda for serverless scaling
- [ ] Integrate with payment gateway APIs
- [ ] Add model versioning & A/B testing

---

**Built with** ❤️ **using FastAPI, XGBoost, React, and Docker**

```
███████╗██████╗  █████╗ ██╗   ██╗██████╗ ███████╗██╗  ██╗██╗███████╗██╗     ██████╗ 
██╔════╝██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗
█████╗  ██████╔╝███████║██║   ██║██║  ██║███████╗███████║██║█████╗  ██║     ██║  ██║
██╔══╝  ██╔══██╗██╔══██║██║   ██║██║  ██║╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║
██║     ██║  ██║██║  ██║╚██████╔╝██████╔╝███████║██║  ██║██║███████╗███████╗██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ 
```
