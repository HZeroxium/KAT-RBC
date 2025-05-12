# /src/agents/spec_analysis_agent.py

from typing import Optional, List
from .base_agent import BaseAgent, AgentInput, AgentOutput
from schemas.index import ParsedSpec
from schemas.system_io import OASSpecFile
from schemas.dependency import (
    OperationDependencyGraph as ODGraph,
    OperationSchemaDep,
    SchemaSchemaDep,
)
from tools.parsing import OpenAPIParserTool as SpecLoaderTool
from tools.dependency import ODGConstructorTool
from pathlib import Path


class SpecAnalysisInput(AgentInput):
    spec_path: str
    spec_content: Optional[str] = None


class SpecAnalysisOutput(AgentOutput):
    parsed_spec: ParsedSpec
    odg: ODGraph
    op_schema_deps: List[OperationSchemaDep]
    schema_schema_deps: List[SchemaSchemaDep]


class SpecAnalysisAgent(BaseAgent):
    """Agent responsible for loading and analyzing the API specification"""

    input_class = SpecAnalysisInput

    def __init__(self):
        self.spec_loader = SpecLoaderTool()
        self.odg_constructor = ODGConstructorTool()

    def run(self, input_data: SpecAnalysisInput) -> SpecAnalysisOutput:
        # 1. Load and parse the specification
        spec_loader_input = self.spec_loader.input_class(
            spec_file=OASSpecFile(
                path=Path(input_data.spec_path), content=input_data.spec_content
            )
        )
        spec_output = self.spec_loader.run(spec_loader_input)

        # 2. Construct the Operation Dependency Graph
        odg_input = self.odg_constructor.input_class(
            parsed_spec=spec_output.parsed_spec
        )
        odg_output = self.odg_constructor.run(odg_input)

        # 3. Return combined output
        return SpecAnalysisOutput(
            parsed_spec=spec_output.parsed_spec,
            odg=odg_output.odg,
            op_schema_deps=odg_output.op_schema_deps,
            schema_schema_deps=odg_output.schema_schema_deps,
        )
