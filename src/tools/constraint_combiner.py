# /src/tools/constraint_combiner.py
from .base import BaseTool
from schemas.index import (
    CombinerInput,
    CombinerOutput,
    UnifiedConstraint,
)


class ConstraintCombinerTool(BaseTool[CombinerInput, CombinerOutput]):
    def _generate_mock_data(self, static_constraint, invariant) -> CombinerOutput:
        """Generate mock data for constraint combiner."""
        merged = UnifiedConstraint(
            id="u1",
            expression=static_constraint.expression,
            originating_ids=[
                static_constraint.id,
                invariant.id,
            ],
        )
        return CombinerOutput(unified_constraints=[merged])

    def run(self, payload: CombinerInput) -> CombinerOutput:
        return self._generate_mock_data(
            payload.static_constraints[0], payload.invariants[0]
        )
