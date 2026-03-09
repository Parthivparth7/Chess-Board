from __future__ import annotations

import logging

from agentic_genomic_ai.models.cancer_expression_model import CancerExpressionModel
from agentic_genomic_ai.models.gene_network_gnn import GeneNetworkGNN
from agentic_genomic_ai.models.splice_detection_model import SpliceDetectionModel
from agentic_genomic_ai.models.tf_binding_model import TFBindingModel

logger = logging.getLogger(__name__)


class MLPredictionAgent:
    """Aggregate genomic ML tasks into a unified prediction bundle."""

    def __init__(self) -> None:
        self.splice_model = SpliceDetectionModel()
        self.cancer_model = CancerExpressionModel()
        self.tf_model = TFBindingModel()
        self.network_model = GeneNetworkGNN()

    def run(self, qc_metrics: dict, features: dict, variant_risk: dict | None = None) -> dict:
        nt_dist = features.get("nucleotide_distribution", {})
        feature_vector = features.get("feature_vector", [])
        kmer_features = features.get("kmer_features", {})

        splice = self.splice_model.predict(nt_dist, float(qc_metrics.get("gc_content_mean", 0.0)))
        cancer = self.cancer_model.predict(
            float(qc_metrics.get("quality_mean", 0.0)),
            float(qc_metrics.get("gc_content_mean", 0.0)),
            feature_vector,
        )
        tf_binding = self.tf_model.predict(kmer_features)
        network = self.network_model.predict(variant_risk or {}, splice, tf_binding)

        result = {
            "splice_detection": splice,
            "cancer_expression": cancer,
            "tf_binding": tf_binding,
            "gene_network": network,
        }
        logger.info("MLPredictionAgent generated multi-task predictions")
        return result
