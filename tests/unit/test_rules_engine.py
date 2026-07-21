from instream_rules import RuleDefinition, RulesEngine


def _rule(**overrides) -> RuleDefinition:
    base = dict(
        id="bank_statement_recency",
        version=1,
        applies_to={"doc_type": "bank_statement"},
        condition={"op": "lte", "field": "document.age_days", "value": 90},
        on_fail={"severity": "FAIL", "message": "too old"},
        on_pass={"severity": "PASS", "message": "ok"},
    )
    base.update(overrides)
    return RuleDefinition.model_validate(base)


def test_rule_passes_when_condition_holds():
    engine = RulesEngine()
    context = {"doc_type": "bank_statement", "document": {"age_days": 10}}
    results = engine.evaluate(context, [_rule()])
    assert len(results) == 1
    assert results[0].status.value == "PASS"


def test_rule_fails_when_condition_violated():
    engine = RulesEngine()
    context = {"doc_type": "bank_statement", "document": {"age_days": 200}}
    results = engine.evaluate(context, [_rule()])
    assert results[0].status.value == "FAIL"
    assert results[0].message == "too old"


def test_rule_does_not_apply_to_other_doc_types():
    engine = RulesEngine()
    context = {"doc_type": "passport", "document": {"age_days": 200}}
    results = engine.evaluate(context, [_rule()])
    assert results == []


def test_composite_and_or_not_conditions():
    engine = RulesEngine()
    rule = _rule(
        condition={
            "op": "and",
            "clauses": [
                {"op": "eq", "field": "doc_type", "value": "bank_statement"},
                {"op": "not", "clauses": [{"op": "gt", "field": "document.age_days", "value": 90}]},
            ],
        }
    )
    passing_context = {"doc_type": "bank_statement", "document": {"age_days": 5}}
    failing_context = {"doc_type": "bank_statement", "document": {"age_days": 200}}

    assert engine.evaluate(passing_context, [rule])[0].status.value == "PASS"
    assert engine.evaluate(failing_context, [rule])[0].status.value == "FAIL"
