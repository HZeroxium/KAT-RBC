# /src/schemas/index.py

from .base import JSON
from typing import Dict, List
from pydantic import BaseModel, HttpUrl
from .system_io import OASSpecFile, HTTPResponse
from .spec_loader import (
    ParsedSpec,
    Operation,
)
from .dependency_graph import (
    OperationDependencyGraph,
    OperationSchemaDep,
    SchemaSchemaDep,
    OperationSequence,
)
from .constraints_miner import (
    StaticConstraint,
    DynamicInvariant,
    UnifiedConstraint,
)

from .test_generation import (
    TestDataFile,
    GeneratedTestCode,
    VerifiedTestCode,
)

from .test_execution import (
    DashboardArtifact,
    TestResults,
)

from .rl import (
    ReinforcementUpdate,
)

# ------------------------------------------------------------------------
# 7. Component-specific I/O wrappers
#    (typed envelopes for LangGraph or ADK state transitions)
# ------------------------------------------------------------------------


class SpecLoaderInput(BaseModel):
    spec_file: OASSpecFile


class SpecLoaderOutput(BaseModel):
    parsed_spec: ParsedSpec


class ODGConstructorInput(BaseModel):
    parsed_spec: ParsedSpec


class ODGConstructorOutput(BaseModel):
    odg: OperationDependencyGraph
    op_schema_deps: List[OperationSchemaDep]
    schema_schema_deps: List[SchemaSchemaDep]


class StaticMinerInput(BaseModel):
    parsed_spec: ParsedSpec


class StaticMinerOutput(BaseModel):
    constraints: List[StaticConstraint]


class DynamicMinerInput(BaseModel):
    execution_logs: List[HTTPResponse]


class DynamicMinerOutput(BaseModel):
    invariants: List[DynamicInvariant]


class CombinerInput(BaseModel):
    static_constraints: List[StaticConstraint]
    invariants: List[DynamicInvariant]


class CombinerOutput(BaseModel):
    unified_constraints: List[UnifiedConstraint]


class DataGenInput(BaseModel):
    operation: Operation
    os_deps: List[OperationSchemaDep]
    ss_deps: List[SchemaSchemaDep]
    parsed_spec: ParsedSpec


class DataGenOutput(BaseModel):
    valid_file: TestDataFile
    invalid_file: TestDataFile
    validation_script: GeneratedTestCode


class ScriptGenInput(BaseModel):
    operation_sequence: OperationSequence
    constraints: List[UnifiedConstraint]
    data_files: List[TestDataFile]


class ScriptGenOutput(BaseModel):
    test_scripts: List[GeneratedTestCode]


class SemanticVerifierInput(BaseModel):
    generated_tests: List[GeneratedTestCode]
    spec_examples: Dict[str, JSON]  # op_id → example JSON


class SemanticVerifierOutput(BaseModel):
    verified_tests: List[VerifiedTestCode]


class TestExecutorInput(BaseModel):
    test_code: List[VerifiedTestCode]
    target_base_url: HttpUrl


class TestExecutorOutput(BaseModel):
    results: TestResults


class ReinforcementInput(BaseModel):
    test_results: TestResults


class ReinforcementOutput(BaseModel):
    update: ReinforcementUpdate


class ReporterInput(BaseModel):
    results: TestResults


class ReporterOutput(BaseModel):
    dashboard: DashboardArtifact
