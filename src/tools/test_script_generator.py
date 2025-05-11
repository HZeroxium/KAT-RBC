# /src/tools/test_script_generator.py
from .base import BaseTool
from schemas.index import (
    ScriptGenInput,
    ScriptGenOutput,
    GeneratedTestCode,
)


class TestScriptGeneratorTool(BaseTool[ScriptGenInput, ScriptGenOutput]):
    def _generate_mock_data(self, sequence_id) -> ScriptGenOutput:
        """Generate mock test scripts."""
        code = GeneratedTestCode(
            operation_sequence_id=sequence_id,
            language="python",
            content="# mock pytest suite\n\ndef test_dummy():\n    assert True",
        )
        return ScriptGenOutput(test_scripts=[code])

    def run(self, payload: ScriptGenInput) -> ScriptGenOutput:
        return self._generate_mock_data(payload.operation_sequence.sequence_id)
