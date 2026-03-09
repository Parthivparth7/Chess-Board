from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerationAgent:
    def __init__(self, reports_dir: str = "reports") -> None:
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self, qc_metrics: dict, model_prediction: dict) -> str:
        summary = (
            f"QC read_count={qc_metrics.get('read_count')}, "
            f"avg_length={qc_metrics.get('avg_read_length')}, "
            f"gc_mean={qc_metrics.get('gc_content_mean')}%. "
            f"Model prediction={model_prediction.get('prediction_label')} "
            f"(confidence={model_prediction.get('confidence')})."
        )
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out = self.reports_dir / f"analysis_{ts}.txt"
        out.write_text(summary)
        logger.info("ReportGenerationAgent wrote report %s", out)
        return summary
