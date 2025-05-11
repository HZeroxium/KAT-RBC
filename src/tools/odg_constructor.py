# /src/tools/odg_constructor.py
import uuid
from .base import BaseTool
from schemas.index import (
    ODGConstructorInput,
    ODGConstructorOutput,
    OperationDependencyGraph,
    OperationSchemaDep,
    SchemaSchemaDep,
)

from schemas.dependency_graph import ODGEdge


class ODGConstructorTool(BaseTool[ODGConstructorInput, ODGConstructorOutput]):
    def _generate_mock_data(self, operations) -> ODGConstructorOutput:
        """Generate mock data for ODG constructor."""
        odg = OperationDependencyGraph(
            nodes=operations,
            edges=[
                ODGEdge(
                    src_operation_id=operations[0],
                    dst_operation_id=operations[0],  # self-loop just for mock
                    reason="Mock edge",
                )
            ],
        )

        return ODGConstructorOutput(
            odg=odg,
            op_schema_deps=[
                OperationSchemaDep(
                    operation_id=operations[0], schema_name="Flight", param_to_field={}
                )
            ],
            schema_schema_deps=[
                SchemaSchemaDep(parent_schema="Flight", child_schema="Flight")
            ],
        )

    def run(self, payload: ODGConstructorInput) -> ODGConstructorOutput:
        ops = [op.operation_id for op in payload.parsed_spec.operations]
        return self._generate_mock_data(ops)
