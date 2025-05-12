# /src/core/dependency/odg_builder.py

"""Operation Dependency Graph builder."""

import re
from typing import Dict, List, Set, Tuple
from schemas.specification import ParsedSpec, Operation
from schemas.dependency import (
    ODGEdge,
    OperationDependencyGraph,
    OperationSchemaDep,
    SchemaSchemaDep,
)


class ODGBuilder:
    """
    Core component for building Operation Dependency Graphs.

    Constructs a graph of API operation dependencies using:
    1. Heuristic analysis of input/output names
    2. LLM-based inference of Operation-Schema and Schema-Schema dependencies
    """

    def __init__(self, llm_client=None):
        """
        Initialize the ODG Builder with an optional language model client.

        Args:
            llm_client: Client for language model API calls
        """
        self.llm_client = llm_client

    def build_graph(
        self, parsed_spec: ParsedSpec
    ) -> Tuple[
        OperationDependencyGraph, List[OperationSchemaDep], List[SchemaSchemaDep]
    ]:
        """
        Build an Operation Dependency Graph from a parsed API specification.

        Args:
            parsed_spec: Structured representation of parsed OpenAPI spec

        Returns:
            Tuple of (operation_dependency_graph, operation_schema_deps, schema_schema_deps)
        """
        # Initialize outputs
        nodes = [op.operation_id for op in parsed_spec.operations]
        edges = []

        # Start with heuristic-based analysis
        heuristic_edges = self._heuristic_analysis(parsed_spec.operations)
        edges.extend(heuristic_edges)

        # Get operation-schema dependencies
        os_deps = self._operation_schema_deps(parsed_spec)

        # Get schema-schema dependencies
        ss_deps = self._schema_schema_deps(parsed_spec)

        # Add LLM-based edges if available
        if self.llm_client:
            llm_edges = self._llm_analysis(parsed_spec, os_deps, ss_deps)
            edges.extend(llm_edges)

        # Create the final graph
        graph = OperationDependencyGraph(nodes=nodes, edges=edges)

        return graph, os_deps, ss_deps

    def _heuristic_analysis(self, operations: List[Operation]) -> List[ODGEdge]:
        """Use heuristics to identify operation dependencies."""
        edges = []
        op_dict = {op.operation_id: op for op in operations}

        # Build a map of primary resources from path patterns
        resources = {}
        for op_id, op in op_dict.items():
            # Extract resource from path (e.g., /flights, /bookings)
            path_parts = op.path.split("/")
            if len(path_parts) > 1:
                resource = path_parts[1].rstrip("s")  # singular form
                if resource:
                    if resource not in resources:
                        resources[resource] = []
                    resources[resource].append(op_id)

        # Connect GET operations to corresponding POST/PUT/PATCH operations
        for resource, ops in resources.items():
            get_ops = [op for op in ops if op_dict[op].method.value == "GET"]
            write_ops = [
                op for op in ops if op_dict[op].method.value in ("POST", "PUT", "PATCH")
            ]

            # GET -> POST/PUT/PATCH (GET info before making changes)
            for get_op in get_ops:
                for write_op in write_ops:
                    edges.append(
                        ODGEdge(
                            src_operation_id=get_op,
                            dst_operation_id=write_op,
                            reason=f"Reading {resource} data before modifying {resource}",
                        )
                    )

            # POST -> GET (create then read)
            post_ops = [op for op in ops if op_dict[op].method.value == "POST"]
            for post_op in post_ops:
                for get_op in get_ops:
                    edges.append(
                        ODGEdge(
                            src_operation_id=post_op,
                            dst_operation_id=get_op,
                            reason=f"Reading {resource} data after creation",
                        )
                    )

        return edges

    def _operation_schema_deps(
        self, parsed_spec: ParsedSpec
    ) -> List[OperationSchemaDep]:
        """Identify dependencies between operations and schemas."""
        os_deps = []

        for op in parsed_spec.operations:
            # Look at each response schema for this operation
            for resp in op.responses:
                if resp.schema_ref and resp.schema_ref.startswith(
                    "#/components/schemas/"
                ):
                    schema_name = resp.schema_ref.split("/")[-1]

                    # Check if schema exists in components
                    if schema_name in parsed_spec.components:
                        # Create a simple mapping (empty for now)
                        os_deps.append(
                            OperationSchemaDep(
                                operation_id=op.operation_id,
                                schema_name=schema_name,
                                param_to_field={},
                            )
                        )

        return os_deps

    def _schema_schema_deps(self, parsed_spec: ParsedSpec) -> List[SchemaSchemaDep]:
        """Identify dependencies between schemas."""
        ss_deps = []
        schemas = parsed_spec.components

        # Simple heuristic: look for properties with types matching schema names
        for schema_name, schema in schemas.items():
            for _, prop in schema.properties.items():
                # Check if the property type matches a schema name
                if prop.type in schemas:
                    ss_deps.append(
                        SchemaSchemaDep(
                            parent_schema=schema_name, child_schema=prop.type
                        )
                    )

                # Look for array types with items referencing schemas
                if (
                    prop.type == "array"
                    and hasattr(prop, "items")
                    and prop.items in schemas
                ):
                    ss_deps.append(
                        SchemaSchemaDep(
                            parent_schema=schema_name, child_schema=prop.items
                        )
                    )

        return ss_deps

    def _llm_analysis(
        self,
        parsed_spec: ParsedSpec,
        os_deps: List[OperationSchemaDep],
        ss_deps: List[SchemaSchemaDep],
    ) -> List[ODGEdge]:
        """Use LLM to identify advanced operation dependencies."""
        # This would use the LLM to analyze operation interactions
        # For demonstration, we'll return an empty list
        return []
