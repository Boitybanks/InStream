import pytest
from instream_shared.types import ValidationResult, ValidationStatus, WorkflowState
from instream_workflow import InvalidTransitionError, WorkflowEngine


def _result(status: ValidationStatus) -> ValidationResult:
    return ValidationResult(rule_id="r", rule_version=1, status=status, message="")


def test_route_to_invalid_when_any_rule_fails():
    engine = WorkflowEngine()
    results = [_result(ValidationStatus.PASS_), _result(ValidationStatus.FAIL)]
    assert engine.route(results, "AUTO") == WorkflowState.ROUTED_INVALID


def test_rule_failure_overrides_high_confidence():
    """AI confidence never overrides a deterministic rule failure."""
    engine = WorkflowEngine()
    results = [_result(ValidationStatus.FAIL)]
    assert engine.route(results, "AUTO") == WorkflowState.ROUTED_INVALID


def test_route_to_review_when_confidence_is_low_but_rules_pass():
    engine = WorkflowEngine()
    results = [_result(ValidationStatus.PASS_)]
    assert engine.route(results, "REVIEW") == WorkflowState.ROUTED_REVIEW


def test_route_to_valid_when_rules_pass_and_confidence_is_auto():
    engine = WorkflowEngine()
    results = [_result(ValidationStatus.PASS_)]
    assert engine.route(results, "AUTO") == WorkflowState.ROUTED_VALID


def test_valid_transition_sequence():
    engine = WorkflowEngine()
    state = WorkflowState.RECEIVED
    state = engine.transition(state, WorkflowState.CLASSIFIED)
    state = engine.transition(state, WorkflowState.VALIDATED)
    state = engine.transition(state, WorkflowState.ROUTED_VALID)
    state = engine.transition(state, WorkflowState.COMPLETED)
    assert state == WorkflowState.COMPLETED


def test_invalid_transition_raises():
    engine = WorkflowEngine()
    with pytest.raises(InvalidTransitionError):
        engine.transition(WorkflowState.RECEIVED, WorkflowState.COMPLETED)
