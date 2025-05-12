# /src/agent/test_execution_agent.py

from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent, AgentInput, AgentOutput
from schemas.test_data import GeneratedTestCode, VerifiedTestCode
from schemas.test_execution import TestResults
from core.execution.test_executor import TestExecutor
import datetime


class TestExecutionInput(AgentInput):
    test_scripts: List[GeneratedTestCode]
    spec_examples: Dict[str, Any]
    target_base_url: str


class TestExecutionOutput(AgentOutput):
    results: TestResults


class TestExecutionAgent(BaseAgent):
    """Agent responsible for executing tests against the API"""

    input_class = TestExecutionInput

    def __init__(self):
        self.test_executor = TestExecutor()

    def run(self, input_data: TestExecutionInput) -> TestExecutionOutput:
        # 1. Convert generated test code to verified test code
        # In a real implementation, this would involve semantic verification
        verified_tests = [
            VerifiedTestCode(
                operation_sequence_id=script.operation_sequence_id,
                language=script.language,
                content=script.content,
                verified_at=datetime.datetime.now(),
            )
            for script in input_data.test_scripts
        ]

        # 2. Execute the tests
        results = self.test_executor.execute_tests(
            verified_tests=verified_tests, api_base_url=input_data.target_base_url
        )

        # 3. Return the results
        return TestExecutionOutput(results=results)
