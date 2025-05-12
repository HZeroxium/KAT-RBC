# /src/workflows/kat_workflow.py

from typing import List, Optional, Dict, Any
from .base_workflow import BaseWorkflow, WorkflowInput, WorkflowOutput
from agents import (
    SpecAnalysisAgent,
    TestGenerationAgent,
    TestExecutionAgent,
    ReportingAgent,
)
from schemas.index import DashboardArtifact, Operation
from schemas.dependency import OperationDependencyGraph as ODGraph


class KATWorkflowInput(WorkflowInput):
    spec_path: str
    spec_content: Optional[str] = None
    target_base_url: str
    spec_examples: Optional[Dict[str, Any]] = None
    save_reports_to: Optional[str] = None


class KATWorkflowOutput(WorkflowOutput):
    dashboard: DashboardArtifact
    odg: ODGraph
    operation_sequences: List[List[Operation]]


class KATWorkflow(BaseWorkflow):
    """
    Workflow focused on Knowledge-Aware API Testing (KAT) approach.
    Primarily focused on operation dependencies and sequence-based testing.
    """

    input_class = KATWorkflowInput

    def __init__(self):
        # Initialize only the agents needed for KAT
        self.spec_analysis = SpecAnalysisAgent()
        self.test_generation = TestGenerationAgent()
        self.test_execution = TestExecutionAgent()
        self.reporting = ReportingAgent()

    def run(self, input_data: KATWorkflowInput) -> KATWorkflowOutput:
        # 1. Analyze API specification (with ODG focus)
        spec_analysis_output = self.spec_analysis.run(
            self.spec_analysis.input_class(
                spec_path=input_data.spec_path, spec_content=input_data.spec_content
            )
        )

        # 2. Generate test cases (with empty constraints for KAT-only approach)
        test_generation_output = self.test_generation.run(
            self.test_generation.input_class(
                parsed_spec=spec_analysis_output.parsed_spec,
                odg=spec_analysis_output.odg,
                op_schema_deps=spec_analysis_output.op_schema_deps,
                schema_schema_deps=spec_analysis_output.schema_schema_deps,
                unified_constraints=[],  # No constraints in KAT-only mode
            )
        )

        # 3. Execute tests
        test_execution_output = self.test_execution.run(
            self.test_execution.input_class(
                test_scripts=test_generation_output.test_scripts,
                spec_examples=input_data.spec_examples or {},
                target_base_url=input_data.target_base_url,
            )
        )

        # 4. Generate reports
        reporting_output = self.reporting.run(
            self.reporting.input_class(
                test_results=test_execution_output.results,
                save_to_path=input_data.save_reports_to,
            )
        )

        # 5. Return the final output with ODG focus
        return KATWorkflowOutput(
            dashboard=reporting_output.dashboard,
            odg=spec_analysis_output.odg,
            operation_sequences=test_generation_output.operation_sequences,
        )
