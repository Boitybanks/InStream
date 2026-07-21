from instream_confidence import ConfidenceEngine


def test_weighted_average_default_strategy():
    engine = ConfidenceEngine()
    result = engine.score({"a": 1.0, "b": 0.5})
    assert result.score == 0.75


def test_weighted_average_with_explicit_weights():
    engine = ConfidenceEngine()
    result = engine.score({"a": 1.0, "b": 0.0}, weights={"a": 3.0, "b": 1.0})
    assert result.score == 0.75


def test_min_critical_strategy():
    engine = ConfidenceEngine()
    result = engine.score(
        {"a": 0.95, "b": 0.4, "c": 0.99},
        strategy="min_critical",
        critical_fields=["a", "c"],
    )
    assert result.score == 0.95


def test_empty_scores_yield_zero():
    engine = ConfidenceEngine()
    result = engine.score({})
    assert result.score == 0.0


def test_classify_thresholds():
    engine = ConfidenceEngine()
    assert engine.classify(0.95) == "AUTO"
    assert engine.classify(0.7) == "REVIEW"
    assert engine.classify(0.3) == "FAIL"
    assert engine.classify(0.5, {"auto": 0.8, "review": 0.4}) == "REVIEW"
