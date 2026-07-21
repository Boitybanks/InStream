from __future__ import annotations

import operator
from typing import Any, Callable

from instream_shared.errors import ConfigError
from instream_shared.types import ValidationResult, ValidationStatus

from instream_rules.dsl import ConditionNode, RuleDefinition

_COMPARISON_OPS: dict[str, Callable[[Any, Any], bool]] = {
    "eq": operator.eq,
    "ne": operator.ne,
    "lt": operator.lt,
    "lte": operator.le,
    "gt": operator.gt,
    "gte": operator.ge,
    "in": lambda actual, expected: actual in expected,
    "not_in": lambda actual, expected: actual not in expected,
    "exists": lambda actual, _expected: actual is not None,
}


def resolve_field(context: dict, dotted_path: str) -> Any:
    value: Any = context
    for part in dotted_path.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = getattr(value, part, None)
    return value


def evaluate_condition(node: ConditionNode, context: dict) -> bool:
    if node.op == "and":
        return all(evaluate_condition(clause, context) for clause in node.clauses or [])
    if node.op == "or":
        return any(evaluate_condition(clause, context) for clause in node.clauses or [])
    if node.op == "not":
        clauses = node.clauses or []
        if not clauses:
            raise ConfigError("'not' condition requires exactly one clause")
        return not evaluate_condition(clauses[0], context)

    comparator = _COMPARISON_OPS.get(node.op)
    if comparator is None:
        raise ConfigError(f"Unknown rule operator: {node.op!r}")
    if node.field is None:
        raise ConfigError(f"Comparison operator {node.op!r} requires a 'field'")
    actual = resolve_field(context, node.field)
    return comparator(actual, node.value)


class RulesEngine:
    """Deterministic. Every call with the same (context, rules) returns the
    same result — no network calls, no AI, nothing non-reproducible.
    """

    def evaluate(self, context: dict, rules: list[RuleDefinition]) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        for rule in rules:
            if not self._applies(rule, context):
                continue
            passed = evaluate_condition(rule.condition, context)
            outcome = rule.on_pass if passed else rule.on_fail
            results.append(
                ValidationResult(
                    rule_id=rule.id,
                    rule_version=rule.version,
                    status=ValidationStatus(outcome.severity),
                    message=outcome.message,
                )
            )
        return results

    @staticmethod
    def _applies(rule: RuleDefinition, context: dict) -> bool:
        return all(resolve_field(context, key) == expected for key, expected in rule.applies_to.items())
