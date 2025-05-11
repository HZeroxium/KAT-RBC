# /src/tools/static_constraint_miner.py
from .base import BaseTool
from schemas.index import (
    StaticMinerInput,
    StaticMinerOutput,
    StaticConstraint,
)
from schemas.base import HTTPMethod


class StaticConstraintMinerTool(BaseTool[StaticMinerInput, StaticMinerOutput]):
    def _generate_mock_data(self, operation) -> StaticMinerOutput:
        """Generate mock data for static constraint miner."""
        c = StaticConstraint(
            id="c1",
            endpoint=operation.path,
            method=operation.method,
            expression="response.status_code == 200",
            details="Mock constraint",
        )
        return StaticMinerOutput(constraints=[c])

    def run(self, payload: StaticMinerInput) -> StaticMinerOutput:
        op = payload.parsed_spec.operations[0]
        return self._generate_mock_data(op)
