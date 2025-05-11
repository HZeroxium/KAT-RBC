# /src/tools/operation_sequencer.py
import uuid
from .base import BaseTool
from schemas.index import (
    OperationSequence,
    OperationDependencyGraph,
)


class OperationSequencerTool(BaseTool[OperationDependencyGraph, OperationSequence]):
    def _generate_mock_data(self, nodes) -> OperationSequence:
        """Generate mock operation sequence."""
        return OperationSequence(sequence_id=str(uuid.uuid4()), operations=nodes)

    def run(self, payload: OperationDependencyGraph) -> OperationSequence:
        return self._generate_mock_data(payload.nodes)
