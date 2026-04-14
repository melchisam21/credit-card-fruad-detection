"""
config.py — Centralized application configuration.

Uses pydantic-settings so every value can be overridden by environment
variables or a .env file without touching source code (12-factor app).
"""

from pydantic_settings import BaseSettings
from pathlib import Path

# Resolve the project root (one level above this file's parent directory)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Credit Card Fraud Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Model artefacts ───────────────────────────────────────────────────────
    MODEL_PATH: Path = BASE_DIR / "models" / "xgb_best_model.pkl"
    SCALER_PATH: Path = BASE_DIR / "models" / "scaler.pkl"
    FEATURES_PATH: Path = BASE_DIR / "models" / "features.json"

    # ── Inference ─────────────────────────────────────────────────────────────
    # Transactions whose fraud probability exceeds this threshold are flagged.
    FRAUD_THRESHOLD: float = 0.7

    # ── Logging / DB ──────────────────────────────────────────────────────────
    LOG_DB_PATH: Path = BASE_DIR / "logs" / "predictions.db"

    # ── CORS ──────────────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000" # Use comma-separated list of origins if needed

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton — import this everywhere instead of re-instantiating.
settings = Settings()
