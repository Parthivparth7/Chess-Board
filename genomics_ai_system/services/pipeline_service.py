from __future__ import annotations

import importlib
import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Any, AsyncIterator, Callable

import httpx
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class PipelineStageError(RuntimeError):
    """Raised when a required pipeline stage cannot be resolved or executed."""


class DataSourceError(RuntimeError):
    """Raised when FASTQ data cannot be fetched from an external source."""


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
        return self._run_pipeline_for_path(tmp_path)

    async def analyze_fastq_stream(self, fastq_file: UploadFile) -> AsyncIterator[str]:
        suffix = Path(fastq_file.filename or "input.fastq").suffix or ".fastq"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await fastq_file.read())
            tmp_path = Path(tmp.name)

        logger.info("Uploaded FASTQ saved for streaming: %s", tmp_path)

        yield self._to_ndjson({"event": "start", "message": "FASTQ upload received", "fastq_path": str(tmp_path)})

        try:
            preprocessed, t1 = self._run_timed_stage_with_elapsed("preprocessing", tmp_path)
            yield self._to_ndjson({"event": "stage_complete", "stage": "preprocessing", "elapsed_sec": round(t1, 4)})

            qc_metrics, t2 = self._run_timed_stage_with_elapsed("qc_analysis", preprocessed)
            yield self._to_ndjson(
                {
                    "event": "stage_complete",
                    "stage": "qc_analysis",
                    "elapsed_sec": round(t2, 4),
                    "qc_metrics": qc_metrics,
                }
            )

            model_results, t3 = self._run_timed_stage_with_elapsed("model_analytics", qc_metrics)
            yield self._to_ndjson(
                {
                    "event": "stage_complete",
                    "stage": "model_analytics",
                    "elapsed_sec": round(t3, 4),
                    "model_results": model_results,
                }
            )

            analysis_summary, t4 = self._run_timed_stage_with_elapsed("analysis_report", model_results)
            yield self._to_ndjson(
                {
                    "event": "stage_complete",
                    "stage": "analysis_report",
                    "elapsed_sec": round(t4, 4),
                    "analysis_summary": str(analysis_summary),
                }
            )

            chatbot_response, t5 = self._run_timed_stage_with_elapsed("chatbot_interface", analysis_summary)
            final_payload = {
                "qc_metrics": qc_metrics if isinstance(qc_metrics, dict) else {"value": qc_metrics},
                "model_results": model_results if isinstance(model_results, dict) else {"value": model_results},
                "analysis_summary": str(analysis_summary),
                "chatbot_response": str(chatbot_response),
            }
            yield self._to_ndjson(
                {
                    "event": "stage_complete",
                    "stage": "chatbot_interface",
                    "elapsed_sec": round(t5, 4),
                    "chatbot_response": str(chatbot_response),
                }
            )
            yield self._to_ndjson({"event": "complete", "result": final_payload})
        except Exception as exc:
            logger.exception("Streaming pipeline failed")
            yield self._to_ndjson({"event": "error", "error": str(exc)})
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Failed to delete temp file: %s", tmp_path)

    async def analyze_fastq_from_url(self, fastq_url: str, filename: str | None = None) -> dict[str, Any]:
        output_name = filename or Path(fastq_url).name or "downloaded.fastq.gz"
        suffix = Path(output_name).suffix or ".fastq"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = Path(tmp.name)

        start = time.perf_counter()
        try:
            timeout = httpx.Timeout(60.0, connect=20.0)
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                async with client.stream("GET", fastq_url) as response:
                    response.raise_for_status()
                    with tmp_path.open("wb") as handle:
                        async for chunk in response.aiter_bytes():
                            handle.write(chunk)
        except Exception as exc:
            tmp_path.unlink(missing_ok=True)
            raise DataSourceError(f"Unable to download FASTQ from URL: {fastq_url}") from exc

        elapsed = time.perf_counter() - start
        logger.info("Downloaded FASTQ from URL in %.4fs: %s", elapsed, fastq_url)
        return self._run_pipeline_for_path(tmp_path)

    async def analyze_fastq_from_ena(self, run_accession: str) -> dict[str, Any]:
        ena_api = (
            "https://www.ebi.ac.uk/ena/portal/api/filereport"
            f"?accession={run_accession}&result=read_run&fields=fastq_ftp&format=json"
        )
        timeout = httpx.Timeout(30.0, connect=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(ena_api)
                response.raise_for_status()
                rows = response.json()
        except Exception as exc:
            raise DataSourceError(f"Failed to query ENA metadata for accession: {run_accession}") from exc

        if not rows or "fastq_ftp" not in rows[0] or not rows[0]["fastq_ftp"]:
            raise DataSourceError(f"No FASTQ FTP links found for ENA accession: {run_accession}")

        fastq_candidates = [item.strip() for item in rows[0]["fastq_ftp"].split(";") if item.strip()]
        if not fastq_candidates:
            raise DataSourceError(f"No usable FASTQ links parsed for ENA accession: {run_accession}")

        first_link = fastq_candidates[0]
        if first_link.startswith("ftp://"):
            first_link = "https://" + first_link[len("ftp://") :]
        elif not first_link.startswith("http://") and not first_link.startswith("https://"):
            first_link = f"https://{first_link}"

        logger.info("Resolved ENA accession %s to FASTQ URL: %s", run_accession, first_link)
        return await self.analyze_fastq_from_url(first_link)

    def _run_pipeline_for_path(self, fastq_path: Path) -> dict[str, Any]:
        try:
            preprocessed = self._run_timed_stage("preprocessing", fastq_path)
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
                fastq_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Failed to delete temp file: %s", fastq_path)

    def _run_timed_stage(self, stage: str, payload: Any) -> Any:
        fn = self._resolve_stage_callable(stage)
        start = time.perf_counter()
        result = fn(payload)
        elapsed = time.perf_counter() - start
        logger.info("Stage '%s' completed in %.4fs", stage, elapsed)
        return result

    def _run_timed_stage_with_elapsed(self, stage: str, payload: Any) -> tuple[Any, float]:
        fn = self._resolve_stage_callable(stage)
        start = time.perf_counter()
        result = fn(payload)
        elapsed = time.perf_counter() - start
        logger.info("Stage '%s' completed in %.4fs", stage, elapsed)
        return result, elapsed

    def _to_ndjson(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, default=str) + "\n"

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
