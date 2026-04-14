"""
main.py — FastAPI application entry point.

Architecture:
  - Lifespan context manager loads ML artefacts once at startup and provides
    a clean shutdown hook.  This guarantees the model is warm before the
    first request is served.
  - Routes are thin: they delegate all business logic to the service layer
    (predictor.py) and the logging layer (logger.py).
  - CORS middleware is pre-configured for local development; tighten
    `allow_origins` in production.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import (
    TransactionInput,
    PredictionResponse,
    HealthResponse,
    MetricsResponse,
)
from app.services.predictor import predictor
from app.utils.logger import prediction_logger

# ── Logging configuration ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Lifespan: load artefacts once, release on shutdown ───────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI's recommended replacement for @app.on_event("startup").
    Everything before `yield` runs at startup; everything after at shutdown.
    """
    log.info("=== %s v%s starting up ===", settings.APP_NAME, settings.APP_VERSION)
    try:
        predictor.load()          # Heavy I/O happens exactly once
    except RuntimeError as exc:
        log.critical("Failed to load ML artefacts: %s", exc)
        raise SystemExit(1) from exc
    log.info("All artefacts loaded. API is ready.")
    yield
    log.info("=== Application shutting down ===")


# ── Application factory ───────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Real-time credit card fraud detection API powered by XGBoost. "
        "Submit a transaction's 29 anonymised features and receive an instant "
        "fraud probability score and binary classification."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — Secure configuration for production
# Split the FRONTEND_URL string by comma to support multiple origins if needed
origins = [origin.strip() for origin in settings.FRONTEND_URL.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ── Request timing middleware ─────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Inject X-Process-Time header so callers can monitor API latency."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
    return response


# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """
    Returns the operational status of the API and whether the ML artefacts
    have been successfully loaded.  Use this endpoint in load-balancer
    health probes (e.g. Render, ECS, K8s readiness checks).
    """
    return HealthResponse(
        status="healthy" if predictor.is_loaded else "degraded",
        model_loaded=predictor.model is not None,
        scaler_loaded=predictor.scaler is not None,
        version=settings.APP_VERSION,
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict fraud probability for a transaction",
    tags=["Inference"],
)
async def predict(transaction: TransactionInput) -> PredictionResponse:
    """
    Run fraud detection on a single credit card transaction.

    **Input**: All 29 feature values (V1–V28 + scaled_amount).

    **Output**:
    - `fraud` — boolean flag (True = fraudulent above threshold)
    - `probability` — raw model probability (0–1)
    - `threshold_used` — the decision boundary applied
    """
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Service is starting up.",
        )

    try:
        result: PredictionResponse = predictor.predict(transaction)
    except Exception as exc:
        log.exception("Prediction failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model inference failed. Please check input data.",
        ) from exc

    # Persist to audit log (non-blocking failure)
    prediction_logger.log(
        input_data=transaction.model_dump(),
        probability=result.probability,
        fraud=result.fraud,
        threshold_used=result.threshold_used,
    )

    log.info(
        "PREDICT | fraud=%-5s | probability=%.4f",
        result.fraud,
        result.probability,
    )

    return result


@app.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Aggregate prediction metrics",
    tags=["System"],
)
async def metrics() -> MetricsResponse:
    """
    Returns aggregate statistics across all predictions processed since
    the service started.  Useful for dashboards and monitoring.
    """
    stats = prediction_logger.get_metrics()
    return MetricsResponse(**stats)


# ── Global exception handler ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )
