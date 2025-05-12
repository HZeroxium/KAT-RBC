# /src/tools/generation/script_generator.py

from ..base import BaseTool
from schemas.index import (
    ScriptGenInput,
    ScriptGenOutput,
    GeneratedTestCode,
    OperationSequence,
)


class TestScriptGeneratorTool(BaseTool[ScriptGenInput, ScriptGenOutput]):
    """
    Tool for generating test scripts from operation sequences and constraints.
    Combines RBCTest's constraint validation with KAT's operation sequencing.
    """

    input_class = ScriptGenInput

    def _generate_mock_data(
        self, operation_sequence: OperationSequence
    ) -> ScriptGenOutput:
        """Generate mock test scripts."""
        code = GeneratedTestCode(
            operation_sequence_id=operation_sequence.sequence_id,
            language="python",
            content="# mock pytest suite\n\ndef test_dummy():\n    assert True",
        )
        return ScriptGenOutput(test_scripts=[code])

    def run(self, payload: ScriptGenInput) -> ScriptGenOutput:
        return self._generate_mock_data(payload.operation_sequence)
