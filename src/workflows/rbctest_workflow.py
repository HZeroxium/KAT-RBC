# /src/workflows/rbctest_workflow.py

from typing import List, Optional, Dict, Any
from .base_workflow import BaseWorkflow, WorkflowInput, WorkflowOutput
from agents import (
    SpecAnalysisAgent,
    ConstraintMiningAgent,
    TestExecutionAgent,
    ReportingAgent,
)
from schemas.index import (
    DashboardArtifact,
    StaticConstraint,
    DynamicInvariant,
    UnifiedConstraint,
    OperationSequence,
)
from schemas.system_io import HTTPResponse


class RBCTestWorkflowInput(WorkflowInput):
    spec_path: str
    spec_content: Optional[str] = None
    execution_logs: Optional[List[HTTPResponse]] = None
    target_base_url: str
    spec_examples: Optional[Dict[str, Any]] = None
    save_reports_to: Optional[str] = None


class RBCTestWorkflowOutput(WorkflowOutput):
    dashboard: DashboardArtifact
    static_constraints: List[StaticConstraint]
    dynamic_invariants: List[DynamicInvariant]
    unified_constraints: List[UnifiedConstraint]


class RBCTestWorkflow(BaseWorkflow):
    """
    Workflow focused on REST API constraint testing using the RBCTest approach.
    Primarily focused on identifying and validating constraints in API specs.
    """

    input_class = RBCTestWorkflowInput

    def __init__(self):
        # Initialize only the agents needed for RBCTest
        self.spec_analysis = SpecAnalysisAgent()
        self.constraint_mining = ConstraintMiningAgent()
        self.test_execution = TestExecutionAgent()
        self.reporting = ReportingAgent()

        # Custom constraint-focused test generator
        from tools.generation import TestScriptGeneratorTool

        self.test_generator = TestScriptGeneratorTool()

    def run(self, input_data: RBCTestWorkflowInput) -> RBCTestWorkflowOutput:
        # 1. Analyze API specification
        spec_analysis_output = self.spec_analysis.run(
            self.spec_analysis.input_class(
                spec_path=input_data.spec_path, spec_content=input_data.spec_content
            )
        )

        # 2. Mine constraints (static and dynamic)
        constraint_mining_output = self.constraint_mining.run(
            self.constraint_mining.input_class(
                parsed_spec=spec_analysis_output.parsed_spec,
                execution_logs=input_data.execution_logs,
            )
        )

        # 3. Generate constraint tests directly (skip the full test generation agent)
        test_scripts = []
        for operation in spec_analysis_output.parsed_spec.operations:
            # Create an operation sequence with a single operation
            operation_sequence = OperationSequence(
                sequence_id=f"single-{operation.operation_id}",
                operations=[operation.operation_id],
            )

            script_input = self.test_generator.input_class(
                operation_sequence=operation_sequence,  # Pass the proper sequence object
                constraints=constraint_mining_output.unified_constraints,
                data_files=[],  # No data files needed for simple constraint checks
            )
            script_output = self.test_generator.run(script_input)
            test_scripts.extend(script_output.test_scripts)

        # 4. Execute tests
        test_execution_output = self.test_execution.run(
            self.test_execution.input_class(
                test_scripts=test_scripts,
                spec_examples=input_data.spec_examples or {},
                target_base_url=input_data.target_base_url,
            )
        )

        # 5. Generate reports
        reporting_output = self.reporting.run(
            self.reporting.input_class(
                test_results=test_execution_output.results,
                save_to_path=input_data.save_reports_to,
            )
        )

        # 6. Return the final output with constraint focus
        return RBCTestWorkflowOutput(
            dashboard=reporting_output.dashboard,
            static_constraints=constraint_mining_output.static_constraints,
            dynamic_invariants=constraint_mining_output.dynamic_invariants,
            unified_constraints=constraint_mining_output.unified_constraints,
        )
