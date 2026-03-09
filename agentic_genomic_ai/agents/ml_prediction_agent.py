from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class MLPredictionAgent:
    """Lightweight deterministic predictor (backward-compatible default)."""

    def run(self, qc_metrics: dict, features: dict) -> dict:
        read_count = float(qc_metrics.get("read_count", 0))
        gc = float(qc_metrics.get("gc_content_mean", 0.0))
        qmean = float(qc_metrics.get("quality_mean", 0.0))

        read_score = min(read_count / 1_000_000, 1.0)
        gc_balance = max(0.0, 1.0 - min(abs(gc - 50.0) / 50.0, 1.0))
        quality_score = min(qmean / 40.0, 1.0)
        confidence = (0.4 * read_score) + (0.3 * gc_balance) + (0.3 * quality_score)

        label = "stable_profile" if confidence >= 0.75 else "review_required" if confidence >= 0.5 else "low_signal"
        result = {
            "prediction_label": label,
            "confidence": round(confidence, 4),
            "risk_score": round(1 - confidence, 4),
            "task": "genomic_quality_risk_estimation",
        }
        logger.info("MLPredictionAgent result label=%s", label)
        return result
