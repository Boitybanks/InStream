from __future__ import annotations

from instream_shared.errors import InStreamError
from instream_shared.types import ValidationResult, ValidationStatus, WorkflowState

VALID_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.RECEIVED: {WorkflowState.CLASSIFIED},
    WorkflowState.CLASSIFIED: {WorkflowState.VALIDATED},
    WorkflowState.VALIDATED: {
        WorkflowState.ROUTED_VALID,
        WorkflowState.ROUTED_INVALID,
        WorkflowState.ROUTED_REVIEW,
    },
    WorkflowState.ROUTED_VALID: {WorkflowState.COMPLETED},
    WorkflowState.ROUTED_INVALID: {WorkflowState.COMPLETED},
    WorkflowState.ROUTED_REVIEW: {WorkflowState.COMPLETED},
    WorkflowState.COMPLETED: set(),
}


class InvalidTransitionError(InStreamError):
    pass


class WorkflowEngine:
    """A pure state machine. It never talks to a destination connector
    itself — callers (the worker pipeline) execute the side effect for a
    transition and then ask the engine to confirm/advance the state, so the
    engine stays trivially unit-testable.
    """

    def transition(self, current: WorkflowState, target: WorkflowState) -> WorkflowState:
        allowed = VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidTransitionError(f"Cannot transition from {current} to {target}")
        return target

    def route(self, validation_results: list[ValidationResult], confidence_label: str) -> WorkflowState:
        """Decide the post-VALIDATED destination.

        Deterministic rule failures always win over AI/OCR confidence — a
        FAIL from the Rules Engine routes to the exception queue regardless
        of how confident the AI extraction was. AI confidence only decides
        between straight-through processing and human review.
        """
        if any(result.status == ValidationStatus.FAIL for result in validation_results):
            return WorkflowState.ROUTED_INVALID
        if confidence_label != "AUTO":
            return WorkflowState.ROUTED_REVIEW
        return WorkflowState.ROUTED_VALID
