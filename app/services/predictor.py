"""
predictor.py — ML inference service.

Responsibilities:
  1. Load the XGBoost model and StandardScaler once at startup.
  2. Accept a validated TransactionInput, preprocess it, and run inference.
  3. Apply the configurable fraud-probability threshold.
  4. Return a structured PredictionResponse.

Design decisions:
  - A module-level singleton (FraudPredictor) is instantiated at import time
    and injected into routes via FastAPI's dependency injection system.
  - Using predict_proba() rather than predict() gives us a continuous
    probability score, which is more informative and lets callers tune
    the threshold for their risk appetite.
"""

import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.config import settings
from app.schemas import TransactionInput, PredictionResponse

logger = logging.getLogger(__name__)


class FraudPredictor:
    """
    Encapsulates model loading and inference logic.

    The heavy I/O (loading artefact files) happens once in __init__ so that
    individual prediction requests incur no file-system overhead.
    """

    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.feature_names: list[str] = []
        self._loaded = False

    # ── Startup ────────────────────────────────────────────────────────────
    def load(self) -> None:
        """
        Load artefacts from disk.  Called once from the FastAPI lifespan hook.
        Raises RuntimeError if any artefact is missing or corrupt.
        """
        logger.info("Loading ML artefacts …")

        for path, label in [
            (settings.MODEL_PATH, "model"),
            (settings.SCALER_PATH, "scaler"),
            (settings.FEATURES_PATH, "features"),
        ]:
            if not Path(path).exists():
                raise RuntimeError(f"Required artefact not found: {path} ({label})")

        # joblib handles sklearn's internal serialisation format more robustly
        # than plain pickle, especially across minor sklearn version differences.
        self.model = joblib.load(settings.MODEL_PATH)
        logger.info("XGBoost model loaded  ✓")

        self.scaler = joblib.load(settings.SCALER_PATH)
        logger.info("StandardScaler loaded ✓")

        with open(settings.FEATURES_PATH, "r") as f:
            self.feature_names = json.load(f)
        logger.info("Feature list loaded   ✓  (%d features)", len(self.feature_names))

        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    # ── Inference ──────────────────────────────────────────────────────────
    def predict(self, transaction: TransactionInput) -> PredictionResponse:
        """
        Run end-to-end inference for a single transaction.

        Pipeline:
          1. Convert Pydantic model → pandas DataFrame (1 row).
          2. Reorder columns to match training-time feature order.
          3. Scale the `scaled_amount` feature using the fitted scaler.
             (V1–V28 are already PCA-transformed and do not need re-scaling.)
          4. Run model.predict_proba and extract the fraud-class probability.
          5. Apply threshold to produce a binary fraud flag.
        """
        if not self._loaded:
            raise RuntimeError("Model has not been loaded yet.")

        # Step 1 — build a single-row DataFrame from the validated input
        raw: dict = transaction.model_dump()
        df = pd.DataFrame([raw])

        # Step 2 — reorder columns to exactly match training feature order
        df = df[self.feature_names]

        # Step 3 — apply the scaler to `scaled_amount` only
        #   The scaler was fitted on the Amount column alone (1-D).
        #   We reshape to (1,1) for the transform call.
        amount_idx = self.feature_names.index("scaled_amount")
        df.iloc[0, amount_idx] = self.scaler.transform(
            [[df.iloc[0, amount_idx]]]
        )[0][0]

        # Step 4 — predict_proba returns [[prob_legit, prob_fraud]]
        proba_matrix = self.model.predict_proba(df)
        fraud_probability: float = float(proba_matrix[0][1])

        # Step 5 — threshold decision
        is_fraud = fraud_probability >= settings.FRAUD_THRESHOLD

        logger.debug(
            "Prediction — probability=%.4f  fraud=%s  threshold=%.2f",
            fraud_probability,
            is_fraud,
            settings.FRAUD_THRESHOLD,
        )

        return PredictionResponse(
            fraud=is_fraud,
            probability=round(fraud_probability, 6),
            threshold_used=settings.FRAUD_THRESHOLD,
        )


# ── Module-level singleton (loaded lazily via lifespan) ────────────────────
predictor = FraudPredictor()
