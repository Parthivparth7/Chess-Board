from __future__ import annotations

from pydantic import BaseModel, Field


class GenomicsAnalysisResponse(BaseModel):
    qc_metrics: dict
    model_predictions: dict
    variant_risk: dict
    analysis_summary: str
    chatbot_explanation: str
    model_prediction: dict | None = Field(default=None, description="Backward-compatible alias")


class ChatAnswerResponse(BaseModel):
    answer: str
