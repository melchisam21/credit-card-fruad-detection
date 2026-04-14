"""
schemas.py — Pydantic models for request/response validation.

All 29 features are declared explicitly so FastAPI auto-generates
a rich OpenAPI schema with field descriptions that document the API.

Feature legend (standard IEEE credit-card fraud dataset):
  V1–V28  : PCA-transformed anonymised transaction features.
  scaled_amount : StandardScaler-normalised transaction amount.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Annotated


# ── Type alias for PCA feature values (float, range roughly -50 to +50) ──────
PCAFeature = Annotated[float, Field(description="PCA-transformed transaction feature")]


class TransactionInput(BaseModel):
    """
    Input payload for a single credit-card transaction.

    All 28 anonymised PCA features (V1–V28) plus the scaled transaction
    amount must be supplied.  Missing or extra fields raise a 422 error.
    """

    # PCA components — anonymised to protect cardholder privacy
    V1:  PCAFeature = Field(..., example=-1.3598071336738)
    V2:  PCAFeature = Field(..., example=-0.0727811733098497)
    V3:  PCAFeature = Field(..., example=2.53634673796914)
    V4:  PCAFeature = Field(..., example=1.37815522427443)
    V5:  PCAFeature = Field(..., example=-0.338320769942518)
    V6:  PCAFeature = Field(..., example=0.462387777762292)
    V7:  PCAFeature = Field(..., example=0.239598554061257)
    V8:  PCAFeature = Field(..., example=0.0986979012610507)
    V9:  PCAFeature = Field(..., example=0.363786969611213)
    V10: PCAFeature = Field(..., example=0.0907941719789316)
    V11: PCAFeature = Field(..., example=-0.551599533260813)
    V12: PCAFeature = Field(..., example=-0.617800855762348)
    V13: PCAFeature = Field(..., example=-0.991389847235408)
    V14: PCAFeature = Field(..., example=-0.311169353699879)
    V15: PCAFeature = Field(..., example=1.46817697209427)
    V16: PCAFeature = Field(..., example=-0.470400525259478)
    V17: PCAFeature = Field(..., example=0.207971241929242)
    V18: PCAFeature = Field(..., example=0.0257905801985591)
    V19: PCAFeature = Field(..., example=0.403992960255733)
    V20: PCAFeature = Field(..., example=0.251412098239705)
    V21: PCAFeature = Field(..., example=-0.018306777944153)
    V22: PCAFeature = Field(..., example=0.277837575558899)
    V23: PCAFeature = Field(..., example=-0.110473910188767)
    V24: PCAFeature = Field(..., example=0.0669280749146731)
    V25: PCAFeature = Field(..., example=0.128539358273528)
    V26: PCAFeature = Field(..., example=-0.189114843888824)
    V27: PCAFeature = Field(..., example=0.133558376740387)
    V28: PCAFeature = Field(..., example=-0.0210530534538215)

    # Transaction amount, pre-scaled by the same StandardScaler used during
    # training.  Callers should apply the scaler BEFORE sending the amount,
    # OR pass the raw amount and let the API scale it (current behaviour:
    # the API scales internally via predictor.py — this field name is kept
    # consistent with `features.json`).
    scaled_amount: float = Field(
        ...,
        description="StandardScaler-normalised transaction amount.",
        example=149.62,
    )

    model_config = {"extra": "forbid"}   # reject any unknown fields


class PredictionResponse(BaseModel):
    """Response returned by POST /predict."""

    fraud: bool = Field(..., description="True if the transaction is flagged as fraud.")
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model's estimated probability that the transaction is fraudulent.",
    )
    threshold_used: float = Field(
        ...,
        description="Probability threshold applied to produce the fraud flag.",
    )


class HealthResponse(BaseModel):
    """Response returned by GET /health."""

    model_config = {"protected_namespaces": ()}   # suppress 'model_' prefix warning

    status: str
    model_loaded: bool
    scaler_loaded: bool
    version: str


class MetricsResponse(BaseModel):
    """Response returned by GET /metrics."""

    total_predictions: int
    total_fraud_flagged: int
    fraud_rate_percent: float
