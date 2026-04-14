"""
logger.py — Prediction audit logger backed by SQLite.

Every POST /predict call writes one row into the `predictions` table so that:
  - Fraud patterns can be investigated post-hoc.
  - Aggregate metrics (fraud rate, prediction volume) can be queried cheaply.
  - The full input is persisted for model retraining / drift monitoring.

Why SQLite?
  Simple, zero-config, ACID-compliant, and ships with Python's stdlib.
  For production at scale, swap the connection string for Postgres.
"""

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class PredictionLogger:
    """Thin wrapper around an SQLite database for audit logging."""

    def __init__(self) -> None:
        self.db_path = settings.LOG_DB_PATH
        self._init_db()

    # ── Schema bootstrap ──────────────────────────────────────────────────
    def _init_db(self) -> None:
        """Create the database file and schema if they don't exist yet."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp       TEXT    NOT NULL,
                    input_features  TEXT    NOT NULL,   -- JSON-serialised input
                    probability     REAL    NOT NULL,
                    fraud           INTEGER NOT NULL,   -- 0 / 1
                    threshold_used  REAL    NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_fraud
                    ON predictions (fraud)
            """)
        logger.info("Prediction log DB initialised at %s", self.db_path)

    # ── Helpers ───────────────────────────────────────────────────────────
    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    # ── Public API ────────────────────────────────────────────────────────
    def log(
        self,
        input_data: dict,
        probability: float,
        fraud: bool,
        threshold_used: float,
    ) -> None:
        """
        Persist one prediction record.

        Parameters
        ----------
        input_data:     The raw feature dict from the request.
        probability:    Fraud probability returned by the model.
        fraud:          Whether the transaction was flagged.
        threshold_used: The threshold that produced the flag.
        """
        ts = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO predictions
                        (timestamp, input_features, probability, fraud, threshold_used)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (ts, json.dumps(input_data), probability, int(fraud), threshold_used),
                )
            logger.debug("Prediction logged at %s | fraud=%s | p=%.4f", ts, fraud, probability)
        except Exception as exc:
            # Logging failure must never crash the prediction endpoint.
            logger.error("Failed to write prediction log: %s", exc)

    def get_metrics(self) -> dict:
        """
        Return aggregate stats for the GET /metrics endpoint.

        Returns
        -------
        {
            "total_predictions": int,
            "total_fraud_flagged": int,
            "fraud_rate_percent": float,
        }
        """
        try:
            with self._connect() as conn:
                total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
                fraud_count = conn.execute(
                    "SELECT COUNT(*) FROM predictions WHERE fraud = 1"
                ).fetchone()[0]
        except Exception as exc:
            logger.error("Failed to query metrics: %s", exc)
            return {"total_predictions": 0, "total_fraud_flagged": 0, "fraud_rate_percent": 0.0}

        fraud_rate = (fraud_count / total * 100) if total else 0.0
        return {
            "total_predictions": total,
            "total_fraud_flagged": fraud_count,
            "fraud_rate_percent": round(fraud_rate, 4),
        }


# Singleton — shared across all request handlers.
prediction_logger = PredictionLogger()
