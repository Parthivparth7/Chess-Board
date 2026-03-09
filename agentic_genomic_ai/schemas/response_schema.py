from __future__ import annotations

from pydantic import BaseModel


class GenomicsAnalysisResponse(BaseModel):
    qc_metrics: dict
    model_prediction: dict
    analysis_summary: str
    chatbot_explanation: str


class ChatAnswerResponse(BaseModel):
    answer: str
