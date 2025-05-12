# /src/schemas/dependency.py

from typing import Dict, List
from pydantic import BaseModel, Field


class ODGEdge(BaseModel):
    """Directed edge: op_a → op_b (op_b depends on op_a)."""

    src_operation_id: str = Field(
        ..., description="Source operation ID (the prerequisite operation)"
    )
    dst_operation_id: str = Field(
        ..., description="Destination operation ID (the dependent operation)"
    )
    reason: str = Field(
        ..., description="Human-readable explanation of this dependency relationship"
    )


class OperationDependencyGraph(BaseModel):
    nodes: List[str] = Field(
        ..., description="List of operation IDs in the dependency graph"
    )
    edges: List[ODGEdge] = Field(
        ..., description="Dependency relationships between operations"
    )


class OperationSequence(BaseModel):
    """A topologically-sorted chain of operations."""

    sequence_id: str = Field(
        ..., description="Unique identifier for this operation sequence"
    )
    operations: List[str] = Field(
        ..., description="Ordered list of operation IDs to be executed sequentially"
    )


class OperationSequenceCollection(BaseModel):
    """Container for multiple operation sequences."""

    operation_sequences: List[OperationSequence] = Field(
        ..., description="Collection of operation sequences"
    )


class OperationSchemaDep(BaseModel):
    operation_id: str = Field(
        ..., description="ID of the operation that depends on a schema"
    )
    schema_name: str = Field(
        ..., description="Name of the schema that the operation depends on"
    )
    param_to_field: Dict[str, str] = Field(
        ...,
        description="Mapping from operation parameters to schema fields (e.g. 'flightId' → 'id')",
    )


class SchemaSchemaDep(BaseModel):
    parent_schema: str = Field(
        ..., description="Name of the parent schema (prerequisite)"
    )
    child_schema: str = Field(..., description="Name of the child schema (dependent)")
