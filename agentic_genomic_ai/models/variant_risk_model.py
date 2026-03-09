from __future__ import annotations

import math


class VariantRiskModel:
    """Heuristic pathogenicity scorer compatible with FASTQ-only workflows."""

    def predict(self, qc_metrics: dict, features: dict) -> dict:
        q = float(qc_metrics.get("quality_mean", 0.0))
        gc = float(qc_metrics.get("gc_content_mean", 0.0))
        read_count = float(qc_metrics.get("read_count", 0.0))
        nt = features.get("nucleotide_distribution", {})
        g_bias = abs(float(nt.get("G", 0.0)) - 0.25)
        c_bias = abs(float(nt.get("C", 0.0)) - 0.25)

        noise = 1.0 - min(q / 40.0, 1.0)
        gc_deviation = min(abs(gc - 50.0) / 50.0, 1.0)
        depth_penalty = 1.0 - min(math.log10(read_count + 1) / 6.0, 1.0)
        composition_shift = min((g_bias + c_bias) * 2.0, 1.0)

        risk = (0.35 * noise) + (0.30 * gc_deviation) + (0.20 * depth_penalty) + (0.15 * composition_shift)
        tier = "high" if risk >= 0.66 else "moderate" if risk >= 0.33 else "low"
        return {
            "task": "variant_pathogenicity_risk",
            "risk_score": round(risk, 4),
            "risk_tier": tier,
            "estimated_pathogenicity_probability": round(min(0.95, risk + 0.05), 4),
        }
