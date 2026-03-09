from __future__ import annotations

import importlib
import logging
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from fastapi import UploadFile

logger = logging.getLogger(__name__)


class PipelineStageError(RuntimeError):
    """Raised when a required pipeline stage cannot be resolved or executed."""


class GenomicsPipelineService:
    """Service that orchestrates FASTQ analytics pipeline stages without modifying stage modules."""

    def __init__(self) -> None:
        self._stage_cache: dict[str, Callable[..., Any]] = {}

    async def analyze_fastq(self, fastq_file: UploadFile) -> dict[str, Any]:
        suffix = Path(fastq_file.filename or "input.fastq").suffix or ".fastq"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await fastq_file.read())
            tmp_path = Path(tmp.name)

        logger.info("Uploaded FASTQ saved: %s", tmp_path)

        try:
            preprocessed = self._run_timed_stage("preprocessing", tmp_path)
            qc_metrics = self._run_timed_stage("qc_analysis", preprocessed)
            model_results = self._run_timed_stage("model_analytics", qc_metrics)
            analysis_summary = self._run_timed_stage("analysis_report", model_results)
            chatbot_response = self._run_timed_stage("chatbot_interface", analysis_summary)
            return {
                "qc_metrics": qc_metrics if isinstance(qc_metrics, dict) else {"value": qc_metrics},
                "model_results": model_results if isinstance(model_results, dict) else {"value": model_results},
                "analysis_summary": str(analysis_summary),
                "chatbot_response": str(chatbot_response),
            }
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Failed to delete temp file: %s", tmp_path)

    def _run_timed_stage(self, stage: str, payload: Any) -> Any:
        fn = self._resolve_stage_callable(stage)
        start = time.perf_counter()
        result = fn(payload)
        elapsed = time.perf_counter() - start
        logger.info("Stage '%s' completed in %.4fs", stage, elapsed)
        return result

    def _resolve_stage_callable(self, stage: str) -> Callable[..., Any]:
        if stage in self._stage_cache:
            return self._stage_cache[stage]

        candidates: dict[str, list[tuple[str, str]]] = {
            "preprocessing": [
                ("preprocessing", "run_preprocessing"),
                ("preprocessing", "preprocess_fastq"),
                ("genomics_ai_system.pipeline.preprocessing", "run_preprocessing"),
                ("genomics_ai_system.pipeline.preprocessing", "preprocess_fastq"),
            ],
            "qc_analysis": [
                ("preprocessing", "run_qc_analysis"),
                ("preprocessing", "qc_analysis"),
                ("genomics_ai_system.pipeline.preprocessing", "run_qc_analysis"),
                ("genomics_ai_system.pipeline.preprocessing", "qc_analysis"),
            ],
            "model_analytics": [
                ("model_building", "run_model_analytics"),
                ("model_building", "build_model"),
                ("genomics_ai_system.pipeline.model_building", "run_model_analytics"),
                ("genomics_ai_system.pipeline.model_building", "build_model"),
            ],
            "analysis_report": [
                ("analysis_report", "generate_analysis_report"),
                ("analysis_report", "generate_report"),
                ("genomics_ai_system.pipeline.analysis_report", "generate_analysis_report"),
                ("genomics_ai_system.pipeline.report_generation", "generate_report"),
            ],
            "chatbot_interface": [
                ("chatbot_interface", "send_to_chatbot"),
                ("chatbot_interface", "chatbot_response"),
                ("genomics_ai_system.chatbot.chatbot_interface", "send_to_chatbot"),
                ("genomics_ai_system.chatbot.chatbot_engine", "generate_response"),
            ],
        }

        for module_name, attr in candidates.get(stage, []):
            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue

            fn = getattr(module, attr, None)
            if callable(fn):
                self._stage_cache[stage] = fn
                return fn

        raise PipelineStageError(
            f"Could not resolve callable for stage '{stage}'. "
            f"Provide one of the expected functions in the existing modules."
        )
