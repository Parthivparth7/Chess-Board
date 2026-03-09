from __future__ import annotations

import logging

from agentic_genomic_ai.models.variant_risk_model import VariantRiskModel

logger = logging.getLogger(__name__)


class VariantAnalysisAgent:
    def __init__(self) -> None:
        self.model = VariantRiskModel()

    def run(self, qc_metrics: dict, features: dict) -> dict:
        result = self.model.predict(qc_metrics, features)
        logger.info("VariantAnalysisAgent risk_tier=%s", result.get("risk_tier"))
        return result
