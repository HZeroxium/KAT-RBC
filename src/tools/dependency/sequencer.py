# /src/tools/dependency/sequencer.py

import uuid
from ..base import BaseTool
from schemas.index import (
    OperationSequence,
    OperationSequenceCollection,
    OperationDependencyGraph,
)


class OperationSequencerTool(
    BaseTool[OperationDependencyGraph, OperationSequenceCollection]
):
    """
    Tool for sequencing API operations based on dependencies.
    Key component of KAT for generating operation execution sequences.
    """

    input_class = OperationDependencyGraph

    def _generate_mock_data(self, nodes) -> OperationSequenceCollection:
        """Generate mock operation sequences."""
        # Create a single sequence with a unique ID
        seq = OperationSequence(sequence_id=str(uuid.uuid4()), operations=nodes)
        # Return a collection containing this sequence
        return OperationSequenceCollection(operation_sequences=[seq])

    def _use_core_logic(
        self, payload: OperationDependencyGraph
    ) -> OperationSequenceCollection:
        """
        Show how to integrate with core sequencing logic.

        In a real implementation, we would:
        1. Import the core sequencer module
        2. Topologically sort the ODG to form call chains
        3. Return operation sequences
        """
        try:
            # Actually import and use the core sequencer
            from core.dependency.sequencer import OperationSequencer

            # Use the core sequencer to generate sequences
            sequencer = OperationSequencer()
            return sequencer.generate_sequences(payload)
        except Exception as e:
            # Proper error handling would go here
            print(f"Error in core sequencer integration: {e}")
            # Fall back to mock data
            return self._generate_mock_data(payload.nodes)

    def run(self, payload: OperationDependencyGraph) -> OperationSequenceCollection:
        # Use the core logic instead of mock data
        return self._use_core_logic(payload)
