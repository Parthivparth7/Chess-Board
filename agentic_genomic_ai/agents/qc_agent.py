from __future__ import annotations

import logging
import statistics

from agentic_genomic_ai.utils.sequence_utils import gc_content

logger = logging.getLogger(__name__)


class QCAgent:
    def run(self, ingested: dict) -> dict:
        records = ingested["records"]
        read_count = len(records)
        lengths = [len(r["sequence"]) for r in records]
        quality_scores = [q for r in records for q in r["quality"]]
        gc_values = [gc_content(r["sequence"]) for r in records]

        metrics = {
            "read_count": read_count,
            "avg_read_length": round(sum(lengths) / len(lengths), 3) if lengths else 0,
            "min_read_length": min(lengths) if lengths else 0,
            "max_read_length": max(lengths) if lengths else 0,
            "gc_content_mean": round(sum(gc_values) / len(gc_values), 3) if gc_values else 0,
            "quality_mean": round(statistics.mean(quality_scores), 3) if quality_scores else 0,
            "quality_median": round(statistics.median(quality_scores), 3) if quality_scores else 0,
        }
        logger.info("QCAgent metrics computed: read_count=%s", metrics["read_count"])
        return metrics
