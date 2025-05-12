# /src/tools/generation/data_generator.py

from pathlib import Path
from ..base import BaseTool
from schemas.index import (
    DataGenInput,
    DataGenOutput,
    TestDataFile,
    GeneratedTestCode,
)

from schemas.test_data import (
    TestDataItem,
    DataSetKind,
)


class TestDataGeneratorTool(BaseTool[DataGenInput, DataGenOutput]):
    """
    Tool for generating test data based on API operations and schemas.
    Used by both RBCTest (for constraint-based testing) and KAT (for sequence-based testing).
    """

    input_class = DataGenInput

    def _generate_mock_data(self, operation_id) -> DataGenOutput:
        """Generate mock test data files."""
        valid = TestDataFile(
            operation_id=operation_id,
            kind=DataSetKind.VALID,
            items=[TestDataItem(data={"mock": "ok"}, expected_code=200)],
            path=Path(f"mock_valid_{operation_id}.jsonl"),
        )
        invalid = TestDataFile(
            operation_id=operation_id,
            kind=DataSetKind.INVALID,
            items=[TestDataItem(data={}, expected_code=400)],
            path=Path(f"mock_invalid_{operation_id}.jsonl"),
        )
        script = GeneratedTestCode(
            operation_sequence_id="seq1",
            language="python",
            content="# placeholder validation script",
        )
        return DataGenOutput(
            valid_file=valid, invalid_file=invalid, validation_script=script
        )

    def run(self, payload: DataGenInput) -> DataGenOutput:
        op_id = payload.operation.operation_id
        return self._generate_mock_data(op_id)
