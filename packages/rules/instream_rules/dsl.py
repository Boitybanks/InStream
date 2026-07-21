from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class ConditionNode(BaseModel):
    """A node in the deterministic condition tree.

    Leaf nodes compare `field` (dotted path into the evaluation context)
    against `value` using `op`. Composite nodes (`and`/`or`/`not`) recurse
    into `clauses`. There is no branch here that calls out to an LLM —
    that is the whole point of keeping rules deterministic.
    """

    model_config = ConfigDict(extra="forbid")

    op: str
    field: str | None = None
    value: Any | None = None
    clauses: list["ConditionNode"] | None = None


ConditionNode.model_rebuild()


class RuleOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: Literal["PASS", "FAIL", "WARN"]
    message: str = ""


class RuleDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    version: int = 1
    applies_to: dict[str, Any] = {}
    condition: ConditionNode
    on_fail: RuleOutcome
    on_pass: RuleOutcome = RuleOutcome(severity="PASS")
