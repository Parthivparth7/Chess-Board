from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerationAgent:
    def __init__(self, reports_dir: str = "reports") -> None:
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self, qc_metrics: dict, model_predictions: dict, variant_risk: dict) -> str:
        summary = (
            "FASTQ analytics completed. "
            f"Reads={qc_metrics.get('read_count')}, GC={qc_metrics.get('gc_content_mean')}%, "
            f"Qmean={qc_metrics.get('quality_mean')}. "
            f"Variant risk tier={variant_risk.get('risk_tier')} "
            f"(score={variant_risk.get('risk_score')}). "
            f"Splice={model_predictions.get('splice_detection', {}).get('label')}, "
            f"CancerExpr={model_predictions.get('cancer_expression', {}).get('label')}, "
            f"Regulatory={model_predictions.get('tf_binding', {}).get('label')}."
        )
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out = self.reports_dir / f"analysis_{ts}.json"
        out.write_text(
            json.dumps(
                {
                    "qc_metrics": qc_metrics,
                    "model_predictions": model_predictions,
                    "variant_risk": variant_risk,
                    "analysis_summary": summary,
                },
                indent=2,
            )
        )
        logger.info("ReportGenerationAgent wrote report %s", out)
        return summary
