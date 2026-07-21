from __future__ import annotations

from typing import Literal

from instream_shared.types import ConfidenceResult

Strategy = Literal["weighted_average", "min_critical"]


class ConfidenceEngine:
    """Aggregates per-field confidence (from OCR + AI extraction) into a single
    overall score. The strategy and thresholds are configured per customer
    pack (`workflows/*.yaml`) — the same pipeline can be strict for one
    customer and lenient for another without any code change.
    """

    def score(
        self,
        field_scores: dict[str, float],
        *,
        strategy: Strategy = "weighted_average",
        weights: dict[str, float] | None = None,
        critical_fields: list[str] | None = None,
    ) -> ConfidenceResult:
        if not field_scores:
            return ConfidenceResult(score=0.0, breakdown={})

        if strategy == "min_critical":
            fields = critical_fields or list(field_scores)
            relevant = [field_scores[f] for f in fields if f in field_scores]
            overall = min(relevant) if relevant else 0.0
        else:
            weights = weights or {}
            total_weight = sum(weights.get(f, 1.0) for f in field_scores)
            weighted_sum = sum(field_scores[f] * weights.get(f, 1.0) for f in field_scores)
            overall = weighted_sum / total_weight if total_weight else 0.0

        return ConfidenceResult(score=round(overall, 4), breakdown=dict(field_scores))

    @staticmethod
    def classify(score: float, thresholds: dict[str, float] | None = None) -> Literal["AUTO", "REVIEW", "FAIL"]:
        """thresholds: {"auto": 0.9, "review": 0.6} — score below "review" fails outright."""
        thresholds = thresholds or {}
        auto_threshold = thresholds.get("auto", 0.9)
        review_threshold = thresholds.get("review", 0.6)
        if score >= auto_threshold:
            return "AUTO"
        if score >= review_threshold:
            return "REVIEW"
        return "FAIL"
