# /src/tools/dynamic_constraint_miner.py
from .base import BaseTool
from schemas.index import (
    DynamicMinerInput,
    DynamicMinerOutput,
    DynamicInvariant,
)


class DynamicConstraintMinerTool(BaseTool[DynamicMinerInput, DynamicMinerOutput]):
    def _generate_mock_data(self) -> DynamicMinerOutput:
        """Generate mock data for dynamic constraint miner."""
        inv = DynamicInvariant(
            id="inv1",
            variables=["size(response.data)"],
            expression="size(response.data) >= 0",
        )
        return DynamicMinerOutput(invariants=[inv])

    def run(self, payload: DynamicMinerInput) -> DynamicMinerOutput:
        return self._generate_mock_data()
