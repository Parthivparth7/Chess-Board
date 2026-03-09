from __future__ import annotations

from typing import Any


def run_model_analytics(qc_metrics: dict[str, Any]) -> dict[str, Any]:
    """Lightweight rule-based analytics score to keep API operational out-of-the-box."""
    total_reads = float(qc_metrics.get("total_reads", 0))
    q30 = float(qc_metrics.get("q30_percent", 0.0))
    gc = float(qc_metrics.get("gc_percent", 0.0))

    read_score = min(total_reads / 1_000_000, 1.0)
    q_score = min(q30 / 100.0, 1.0)
    gc_penalty = min(abs(gc - 50.0) / 50.0, 1.0)

    confidence = max(0.0, min(1.0, (0.4 * read_score) + (0.5 * q_score) + (0.1 * (1 - gc_penalty))))

    label = "high_quality" if confidence >= 0.8 else "needs_review" if confidence >= 0.5 else "low_quality"

    return {
        "quality_confidence": round(confidence, 4),
        "classification": label,
        "read_depth_score": round(read_score, 4),
        "quality_score": round(q_score, 4),
        "gc_bias_penalty": round(gc_penalty, 4),
    }
