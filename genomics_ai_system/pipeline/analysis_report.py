from __future__ import annotations

from typing import Any


def generate_analysis_report(model_results: dict[str, Any]) -> str:
    label = model_results.get("classification", "unknown")
    confidence = model_results.get("quality_confidence", "n/a")
    return (
        f"FASTQ analytics completed. Classification: {label}. "
        f"Confidence score: {confidence}."
    )
