from __future__ import annotations


class CancerExpressionModel:
    """Estimate cancer-like expression profile probability from sequence-derived proxies."""

    def __init__(self) -> None:
        self._sk_model = None
        self._init_optional_model()

    def _init_optional_model(self) -> None:
        try:
            import numpy as np
            from sklearn.ensemble import GradientBoostingClassifier

            model = GradientBoostingClassifier(random_state=7)
            x = np.array(
                [
                    [0.90, 0.85, 0.80],
                    [0.88, 0.78, 0.76],
                    [0.55, 0.45, 0.30],
                    [0.52, 0.40, 0.25],
                    [0.65, 0.70, 0.55],
                    [0.70, 0.68, 0.60],
                ]
            )
            y = np.array([0, 0, 1, 1, 0, 0])
            model.fit(x, y)
            self._sk_model = model
        except Exception:
            self._sk_model = None

    def predict(self, quality_mean: float, gc_content_mean: float, feature_vector: list[float]) -> dict:
        complexity = 0.0
        if feature_vector:
            m = sum(feature_vector) / len(feature_vector)
            complexity = (sum((v - m) ** 2 for v in feature_vector) / len(feature_vector)) ** 0.5

        quality_score = min(quality_mean / 40.0, 1.0)
        gc_balance = 1.0 - min(abs((gc_content_mean / 100.0) - 0.5) / 0.5, 1.0)
        complexity_score = min(complexity * 10, 1.0)

        if self._sk_model is not None:
            import numpy as np

            x = np.array([[quality_score, gc_balance, complexity_score]])
            proba = float(self._sk_model.predict_proba(x)[0, 1])
        else:
            proba = max(0.0, min(1.0, 0.6 * (1 - quality_score) + 0.2 * (1 - gc_balance) + 0.2 * complexity_score))

        return {
            "task": "cancer_expression_classification",
            "probability_cancer_like": round(proba, 4),
            "label": "cancer_like_pattern" if proba >= 0.5 else "normal_like_pattern",
        }
