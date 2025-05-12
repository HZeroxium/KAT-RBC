# /src/tools/execution/test_executor.py

from ..base import BaseTool
from schemas.index import (
    TestExecutorInput,
    TestExecutorOutput,
    TestResults,
)

from schemas.test_execution import (
    TestOutcome,
    TestStatus,
)


class TestExecutorTool(BaseTool[TestExecutorInput, TestExecutorOutput]):
    """
    Tool for executing test scripts against target APIs.
    Common component used in both RBCTest and KAT frameworks.
    """

    input_class = TestExecutorInput

    def _generate_mock_data(self) -> TestExecutorOutput:
        """Generate mock test execution results."""
        outcome = TestOutcome(
            test_name="test_dummy",
            status=TestStatus.MATCHED,
            expected="200",
            actual="200",
            details="Mock execution pass",
        )
        res = TestResults(suite_id="suite1", outcomes=[outcome])
        return TestExecutorOutput(results=res)

    def run(self, payload: TestExecutorInput) -> TestExecutorOutput:
        return self._generate_mock_data()
