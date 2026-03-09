from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable

from agentic_genomic_ai.agents.chatbot_agent import ChatbotAgent
from agentic_genomic_ai.agents.data_ingestion_agent import DataIngestionAgent
from agentic_genomic_ai.agents.feature_extraction_agent import FeatureExtractionAgent
from agentic_genomic_ai.agents.ml_prediction_agent import MLPredictionAgent
from agentic_genomic_ai.agents.qc_agent import QCAgent
from agentic_genomic_ai.agents.rag_retrieval_agent import RAGRetrievalAgent
from agentic_genomic_ai.agents.report_generation_agent import ReportGenerationAgent
from agentic_genomic_ai.agents.variant_analysis_agent import VariantAnalysisAgent

logger = logging.getLogger(__name__)


class AgenticPipelineOrchestrator:
    def __init__(self) -> None:
        self.data_agent = DataIngestionAgent()
        self.qc_agent = QCAgent()
        self.feature_agent = FeatureExtractionAgent()
        self.variant_agent = VariantAnalysisAgent()
        self.ml_agent = MLPredictionAgent()
        self.report_agent = ReportGenerationAgent()
        self.rag_agent = RAGRetrievalAgent()
        self.chatbot_agent = ChatbotAgent()

    def _stage(self, name: str, fn: Callable[..., Any], *args, **kwargs):
        logger.info("stage=%s status=started", name)
        t0 = time.perf_counter()
        try:
            out = fn(*args, **kwargs)
        except Exception:
            dt = time.perf_counter() - t0
            logger.exception("stage=%s status=error elapsed=%.4fs", name, dt)
            raise
        dt = time.perf_counter() - t0
        logger.info("stage=%s status=ok elapsed=%.4fs", name, dt)
        return out

    def run_fastq_pipeline(self, fastq_path: str | Path, question: str = "Summarize genomic findings") -> dict:
        ingested = self._stage("data_ingestion", self.data_agent.run, fastq_path)
        qc_metrics = self._stage("qc", self.qc_agent.run, ingested)
        features = self._stage("feature_extraction", self.feature_agent.run, ingested)
        variant_risk = self._stage("variant_analysis", self.variant_agent.run, qc_metrics, features)
        model_predictions = self._stage("ml_prediction", self.ml_agent.run, qc_metrics, features, variant_risk)
        analysis_summary = self._stage("report_generation", self.report_agent.run, qc_metrics, model_predictions, variant_risk)
        context = self._stage("rag_retrieval", self.rag_agent.run, f"{question} {analysis_summary}")
        chatbot_explanation = self._stage(
            "chatbot",
            self.chatbot_agent.run,
            question,
            analysis_summary,
            context,
        )
        # Preserve legacy response key `model_prediction` while exposing new contract.
        return {
            "qc_metrics": qc_metrics,
            "model_predictions": model_predictions,
            "model_prediction": model_predictions,
            "variant_risk": variant_risk,
            "analysis_summary": analysis_summary,
            "chatbot_explanation": chatbot_explanation,
        }
