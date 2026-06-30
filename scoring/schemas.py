"""Pydantic schemas for scoring model outputs."""

from typing import List, Optional

from pydantic import BaseModel

from ingestion.schemas import EngagementLabel


class PredictionResult(BaseModel):
    """Output of predict_strength()."""

    hook_text: str
    label: EngagementLabel
    confidence: float  # 0.0 - 1.0, probability of predicted class


class BaselineResult(BaseModel):
    """Metrics for a single baseline predictor."""

    name: str
    accuracy: float
    precision: float
    recall: float
    predictions: List[str]


class HookPredictionDetail(BaseModel):
    """Per-hook prediction detail for evaluation."""

    hook_id: str
    hook_text: str
    true_label: str
    predicted_label: str
    confidence: float


class ModelMetrics(BaseModel):
    """Full evaluation output for one trained model."""

    model_name: str
    accuracy: float
    precision: float
    recall: float
    confusion_matrix: List[List[int]]  # 2x2 as nested list
    test_predictions: List[HookPredictionDetail]


class FailureCase(BaseModel):
    """A single misclassified hook for failure analysis."""

    hook_id: str
    hook_text: str
    true_label: str
    predicted_label: str
    confidence: float
    notes: str = ""


class EvalReport(BaseModel):
    """Top-level evaluation report aggregating all results."""

    baselines: List[BaselineResult]
    models: List[ModelMetrics]
    failure_analysis: List[FailureCase]
    generated_at: str
    dataset_summary: Optional[str] = None
