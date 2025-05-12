# /src/schemas/index.py

from .common import JSON
from typing import Dict, List
from pydantic import BaseModel, HttpUrl, Field
from .system_io import OASSpecFile, HTTPResponse
from .specification import (
    ParsedSpec,
    Operation,
)
from .dependency import (
    OperationDependencyGraph,
    OperationSchemaDep,
    SchemaSchemaDep,
    OperationSequence,
    OperationSequenceCollection,
)
from .constraint import (
    StaticConstraint,
    DynamicInvariant,
    UnifiedConstraint,
)

from .test_data import (
    TestDataFile,
    GeneratedTestCode,
    VerifiedTestCode,
)

from .test_execution import (
    DashboardArtifact,
    TestResults,
)

from .experience_reinforcement import ReinforcementUpdate, PromptTemplate


class SpecLoaderInput(BaseModel):
    spec_file: OASSpecFile = Field(
        ..., description="OpenAPI/Swagger specification file to be processed"
    )


class SpecLoaderOutput(BaseModel):
    parsed_spec: ParsedSpec = Field(
        ..., description="Structured representation of the parsed OpenAPI specification"
    )


class ODGConstructorInput(BaseModel):
    parsed_spec: ParsedSpec = Field(
        ...,
        description="Parsed OpenAPI specification to build Operation Dependency Graph from",
    )


class ODGConstructorOutput(BaseModel):
    odg: OperationDependencyGraph = Field(
        ...,
        description="Operation Dependency Graph representing relationships between API operations",
    )
    op_schema_deps: List[OperationSchemaDep] = Field(
        ..., description="Dependencies between operations and schemas"
    )
    schema_schema_deps: List[SchemaSchemaDep] = Field(
        ..., description="Dependencies between schemas (parent-child relationships)"
    )


class StaticMinerInput(BaseModel):
    parsed_spec: ParsedSpec = Field(
        ..., description="Parsed API specification for mining static constraints"
    )


class StaticMinerOutput(BaseModel):
    constraints: List[StaticConstraint] = Field(
        ..., description="List of static constraints extracted from API specification"
    )


class DynamicMinerInput(BaseModel):
    execution_logs: List[HTTPResponse] = Field(
        ..., description="API execution logs for mining dynamic invariants"
    )


class DynamicMinerOutput(BaseModel):
    invariants: List[DynamicInvariant] = Field(
        ..., description="Dynamically discovered invariants from API execution logs"
    )


class CombinerInput(BaseModel):
    static_constraints: List[StaticConstraint] = Field(
        ..., description="Static constraints extracted from API specification"
    )
    invariants: List[DynamicInvariant] = Field(
        ..., description="Dynamic invariants discovered from execution logs"
    )


class CombinerOutput(BaseModel):
    unified_constraints: List[UnifiedConstraint] = Field(
        ...,
        description="Combined set of constraints from both static and dynamic sources",
    )


class DataGenInput(BaseModel):
    operation: Operation = Field(
        ..., description="API operation to generate test data for"
    )
    os_deps: List[OperationSchemaDep] = Field(
        ..., description="Dependencies between operations and schemas"
    )
    ss_deps: List[SchemaSchemaDep] = Field(
        ..., description="Dependencies between schemas"
    )
    parsed_spec: ParsedSpec = Field(
        ..., description="Complete parsed API specification"
    )


class DataGenOutput(BaseModel):
    valid_file: TestDataFile = Field(
        ..., description="File containing valid test data cases"
    )
    invalid_file: TestDataFile = Field(
        ..., description="File containing invalid test data cases"
    )
    validation_script: GeneratedTestCode = Field(
        ..., description="Python script to validate the generated test data"
    )


class ScriptGenInput(BaseModel):
    operation_sequence: OperationSequence = Field(
        ..., description="Sequence of operations to generate test scripts for"
    )
    constraints: List[UnifiedConstraint] = Field(
        ..., description="Constraints to validate in the generated test scripts"
    )
    data_files: List[TestDataFile] = Field(
        ..., description="Test data files to use in the generated scripts"
    )


class ScriptGenOutput(BaseModel):
    test_scripts: List[GeneratedTestCode] = Field(
        ..., description="Generated test scripts for the operation sequence"
    )


class SemanticVerifierInput(BaseModel):
    generated_tests: List[GeneratedTestCode] = Field(
        ..., description="Test scripts to be semantically verified"
    )
    spec_examples: Dict[str, JSON] = Field(
        ...,
        description="Example responses from the API specification, keyed by operation ID",
    )


class SemanticVerifierOutput(BaseModel):
    verified_tests: List[VerifiedTestCode] = Field(
        ...,
        description="Test scripts that have been validated against specification examples",
    )


class TestExecutorInput(BaseModel):
    test_code: List[VerifiedTestCode] = Field(
        ..., description="Verified test code to execute against the API"
    )
    target_base_url: HttpUrl = Field(
        ..., description="Base URL of the target API endpoint to test"
    )


class TestExecutorOutput(BaseModel):
    results: TestResults = Field(
        ...,
        description="Results of test execution including matched, mismatched, and unknown outcomes",
    )


class ReinforcementInput(BaseModel):
    test_results: TestResults = Field(
        ..., description="Test execution results for reinforcement learning"
    )


class ReinforcementOutput(BaseModel):
    update: ReinforcementUpdate = Field(
        ..., description="Updates to prompts and weights based on test results"
    )


class ReporterInput(BaseModel):
    results: TestResults = Field(..., description="Test execution results to report")


class ReporterOutput(BaseModel):
    dashboard: DashboardArtifact = Field(
        ..., description="Dashboard artifact containing coverage reports and mismatches"
    )
