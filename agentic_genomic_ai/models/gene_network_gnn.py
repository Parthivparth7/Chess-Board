from __future__ import annotations

import math


class GeneNetworkGNN:
    """Lightweight network-prior scorer emulating disease-gene centrality estimation."""

    def predict(self, variant_risk: dict, splice_prediction: dict, tf_prediction: dict) -> dict:
        risk = float(variant_risk.get("risk_score", 0.0))
        splice = float(splice_prediction.get("probability_splice_site", 0.0))
        tfb = float(tf_prediction.get("tf_binding_probability", 0.0))
        centrality = min(1.0, 0.5 * risk + 0.3 * splice + 0.2 * tfb)
        network_impact = 1 / (1 + math.exp(-6 * (centrality - 0.5)))
        return {
            "task": "gene_network_analysis",
            "network_impact_score": round(network_impact, 4),
            "priority": "high" if network_impact >= 0.7 else "medium" if network_impact >= 0.4 else "low",
        }
