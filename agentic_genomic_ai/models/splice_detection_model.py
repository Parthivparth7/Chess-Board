from __future__ import annotations


class SpliceDetectionModel:
    """Predict exon/intron splice-site likelihood from lightweight sequence features."""

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self._sk_model = None
        self._init_optional_model()

    def _init_optional_model(self) -> None:
        try:
            import numpy as np
            from sklearn.ensemble import RandomForestClassifier

            model = RandomForestClassifier(n_estimators=120, random_state=self.random_state)
            x = np.array(
                [
                    [0.62, 0.18, 0.12, 0.08, 0.22],
                    [0.58, 0.21, 0.11, 0.10, 0.20],
                    [0.25, 0.25, 0.26, 0.24, 0.50],
                    [0.20, 0.30, 0.30, 0.20, 0.52],
                    [0.35, 0.15, 0.35, 0.15, 0.65],
                    [0.33, 0.17, 0.34, 0.16, 0.66],
                ]
            )
            y = np.array([1, 1, 0, 0, 0, 0])
            model.fit(x, y)
            self._sk_model = model
        except Exception:
            self._sk_model = None

    def predict(self, nucleotide_distribution: dict[str, float], gc_content_mean: float) -> dict:
        a = float(nucleotide_distribution.get("A", 0.0))
        c = float(nucleotide_distribution.get("C", 0.0))
        g = float(nucleotide_distribution.get("G", 0.0))
        t = float(nucleotide_distribution.get("T", 0.0))
        gc_fraction = gc_content_mean / 100.0

        if self._sk_model is not None:
            import numpy as np

            features = np.array([[a, c, g, t, gc_fraction]])
            proba = float(self._sk_model.predict_proba(features)[0, 1])
        else:
            motif_balance = max(0.0, 1.0 - abs((g + t) - 0.5) * 2)
            proba = max(0.0, min(1.0, 0.55 * motif_balance + 0.45 * (1 - abs(gc_fraction - 0.5))))

        return {
            "task": "splice_site_detection",
            "probability_splice_site": round(proba, 4),
            "label": "splice_site_enriched" if proba >= 0.5 else "no_splice_signal",
        }
