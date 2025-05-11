# /src/main.py
from pathlib import Path
from pprint import pprint
from schemas.index import *
from schemas.system_io import OASSpecFile

from tools import (
    SpecLoaderTool,
    ODGConstructorTool,
    StaticConstraintMinerTool,
    DynamicConstraintMinerTool,
    ConstraintCombinerTool,
    OperationSequencerTool,
    TestDataGeneratorTool,
    TestScriptGeneratorTool,
    SemanticVerifierTool,
    TestExecutorTool,
    ExperienceReinforcementTool,
    ReporterTool,
)

# ------------------------------------------------------------------#
# 1. Create minimal mock inputs
# ------------------------------------------------------------------#

spec_input = SpecLoaderInput(
    spec_file=OASSpecFile(
        path=Path("mock.yaml"),
        content="openapi: 3.1.0\ninfo:\n  title: Mock\n  version: 0.1.0",
    )
)
exec_logs: list[HTTPResponse] = []  # empty for demo

# ------------------------------------------------------------------#
# 2. Instantiate tools (normally orchestrated via LangGraph / ADK)
# ------------------------------------------------------------------#

spec_loader = SpecLoaderTool()
odg_builder = ODGConstructorTool()
static_miner = StaticConstraintMinerTool()
dynamic_miner = DynamicConstraintMinerTool()
combiner = ConstraintCombinerTool()
sequencer = OperationSequencerTool()
data_gen = TestDataGeneratorTool()
script_gen = TestScriptGeneratorTool()
verifier = SemanticVerifierTool()
executor = TestExecutorTool()
reinforce = ExperienceReinforcementTool()
reporter = ReporterTool()

# ------------------------------------------------------------------#
# 3. Run pipeline
# ------------------------------------------------------------------#

spec_out = spec_loader.run(spec_input)
odg_out = odg_builder.run(ODGConstructorInput(parsed_spec=spec_out.parsed_spec))
static_out = static_miner.run(StaticMinerInput(parsed_spec=spec_out.parsed_spec))
dynamic_out = dynamic_miner.run(DynamicMinerInput(execution_logs=exec_logs))
comb_out = combiner.run(
    CombinerInput(
        static_constraints=static_out.constraints,
        invariants=dynamic_out.invariants,
    )
)
seq = sequencer.run(odg_out.odg)
dg_out = data_gen.run(
    DataGenInput(
        operation=spec_out.parsed_spec.operations[0],
        os_deps=odg_out.op_schema_deps,
        ss_deps=odg_out.schema_schema_deps,
        parsed_spec=spec_out.parsed_spec,
    )
)
sg_out = script_gen.run(
    ScriptGenInput(
        operation_sequence=seq,
        constraints=comb_out.unified_constraints,
        data_files=[dg_out.valid_file, dg_out.invalid_file],
    )
)
ver_out = verifier.run(
    SemanticVerifierInput(
        generated_tests=sg_out.test_scripts,
        spec_examples={},
    )
)
exec_out = executor.run(
    TestExecutorInput(
        test_code=ver_out.verified_tests,
        target_base_url="https://api.example.com",
    )
)
reinforce_out = reinforce.run(ReinforcementInput(test_results=exec_out.results))
report = reporter.run(ReporterInput(results=exec_out.results))

# ------------------------------------------------------------------#
# 4. Pretty-print final artefact
# ------------------------------------------------------------------#
pprint(report.dashboard.model_dump(), depth=4)
