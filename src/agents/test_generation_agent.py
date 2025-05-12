# /src/agents/test_execution_agent.py

from typing import List
from .base_agent import BaseAgent, AgentInput, AgentOutput
from schemas.index import ParsedSpec, Operation
from schemas.dependency import (
    OperationDependencyGraph as ODGraph,
    OperationSchemaDep,
    SchemaSchemaDep,
    OperationSequence,
    OperationSequenceCollection,
)
from schemas.constraint import UnifiedConstraint
from tools.dependency import OperationSequencerTool
from tools.generation import TestDataGeneratorTool, TestScriptGeneratorTool
from schemas.test_data import TestDataFile, GeneratedTestCode


class TestGenerationInput(AgentInput):
    parsed_spec: ParsedSpec
    odg: ODGraph
    op_schema_deps: List[OperationSchemaDep]
    schema_schema_deps: List[SchemaSchemaDep]
    unified_constraints: List[UnifiedConstraint]


class TestGenerationOutput(AgentOutput):
    test_scripts: List[GeneratedTestCode]  # Changed from List[str]
    valid_data_files: List[TestDataFile]  # Changed from List[Path]
    invalid_data_files: List[TestDataFile]  # Changed from List[Path]
    operation_sequences: List[OperationSequence]  # Changed from List[List[Operation]]


class TestGenerationAgent(BaseAgent):
    """Agent responsible for generating test sequences, test data and test scripts"""

    input_class = TestGenerationInput

    def __init__(self):
        self.sequencer = OperationSequencerTool()
        self.data_generator = TestDataGeneratorTool()
        self.script_generator = TestScriptGeneratorTool()

    def run(self, input_data: TestGenerationInput) -> TestGenerationOutput:
        # 1. Generate operation sequences
        sequences = self.sequencer.run(input_data.odg)

        # 2. Generate test data for each operation
        valid_files = []
        invalid_files = []

        for operation in input_data.parsed_spec.operations:
            data_gen_input = self.data_generator.input_class(
                operation=operation,
                os_deps=input_data.op_schema_deps,
                ss_deps=input_data.schema_schema_deps,
                parsed_spec=input_data.parsed_spec,
            )
            data_gen_output = self.data_generator.run(data_gen_input)

            valid_files.append(data_gen_output.valid_file)
            invalid_files.append(data_gen_output.invalid_file)

        # 3. Generate test scripts
        all_test_scripts = []

        for sequence in sequences.operation_sequences:
            script_gen_input = self.script_generator.input_class(
                operation_sequence=sequence,
                constraints=input_data.unified_constraints,
                data_files=valid_files + invalid_files,
            )
            script_gen_output = self.script_generator.run(script_gen_input)
            all_test_scripts.extend(script_gen_output.test_scripts)

        # 4. Return the results
        return TestGenerationOutput(
            test_scripts=all_test_scripts,
            valid_data_files=valid_files,
            invalid_data_files=invalid_files,
            operation_sequences=sequences.operation_sequences,
        )
