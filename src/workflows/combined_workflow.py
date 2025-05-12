# /src/workflows/combined_workflow.py

from typing import List, Optional, Dict, Any
from .base_workflow import BaseWorkflow, WorkflowInput, WorkflowOutput
from agents import (
    SpecAnalysisAgent,
    ConstraintMiningAgent,
    TestGenerationAgent,
    TestExecutionAgent,
    ReportingAgent,
)
from schemas.index import DashboardArtifact as Dashboard
from schemas.system_io import HTTPResponse


class CombinedWorkflowInput(WorkflowInput):
    spec_path: str
    spec_content: Optional[str] = None
    execution_logs: Optional[List[HTTPResponse]] = None
    target_base_url: str
    spec_examples: Optional[Dict[str, Any]] = None
    save_reports_to: Optional[str] = None


class CombinedWorkflowOutput(WorkflowOutput):
    dashboard: Dashboard
    refined_prompts: dict
    updated_weights: dict


class CombinedTestingWorkflow(BaseWorkflow):
    """
    Main workflow that combines RBCTest and KAT approaches for
    comprehensive API testing.
    """

    input_class = CombinedWorkflowInput

    def __init__(self):
        # Initialize all required agents
        self.spec_analysis = SpecAnalysisAgent()
        self.constraint_mining = ConstraintMiningAgent()
        self.test_generation = TestGenerationAgent()
        self.test_execution = TestExecutionAgent()
        self.reporting = ReportingAgent()

    def run(self, input_data: CombinedWorkflowInput) -> CombinedWorkflowOutput:
        # 1. Analyze API specification
        spec_analysis_output = self.spec_analysis.run(
            self.spec_analysis.input_class(
                spec_path=input_data.spec_path, spec_content=input_data.spec_content
            )
        )

        # 2. Mine constraints (static and dynamic if logs available)
        constraint_mining_output = self.constraint_mining.run(
            self.constraint_mining.input_class(
                parsed_spec=spec_analysis_output.parsed_spec,
                execution_logs=input_data.execution_logs,
            )
        )

        # 3. Generate test cases
        test_generation_output = self.test_generation.run(
            self.test_generation.input_class(
                parsed_spec=spec_analysis_output.parsed_spec,
                odg=spec_analysis_output.odg,
                op_schema_deps=spec_analysis_output.op_schema_deps,
                schema_schema_deps=spec_analysis_output.schema_schema_deps,
                unified_constraints=constraint_mining_output.unified_constraints,
            )
        )

        # 4. Execute tests
        test_execution_output = self.test_execution.run(
            self.test_execution.input_class(
                test_scripts=test_generation_output.test_scripts,
                spec_examples=input_data.spec_examples or {},
                target_base_url=input_data.target_base_url,
            )
        )

        # 5. Generate reports and improve for future runs
        reporting_output = self.reporting.run(
            self.reporting.input_class(
                test_results=test_execution_output.results,
                save_to_path=input_data.save_reports_to,
            )
        )

        # 6. Return the final output
        return CombinedWorkflowOutput(
            dashboard=reporting_output.dashboard,
            refined_prompts=reporting_output.refined_prompts,
            updated_weights=reporting_output.updated_weights,
        )
