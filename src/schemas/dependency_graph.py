# /src/schemas/dependency_graph.py

from typing import Dict, List
from pydantic import BaseModel


class ODGEdge(BaseModel):
    """Directed edge: op_a → op_b (op_b depends on op_a)."""

    src_operation_id: str
    dst_operation_id: str
    reason: str  # human-readable explanation from GPT


class OperationDependencyGraph(BaseModel):
    nodes: List[str]  # operation_ids
    edges: List[ODGEdge]  # dependency relations


class OperationSequence(BaseModel):
    """A topologically-sorted chain of operations."""

    sequence_id: str
    operations: List[str]  # ordered operation_ids


class OperationSchemaDep(BaseModel):
    operation_id: str
    schema_name: str
    param_to_field: Dict[str, str]  # request param → schema field


class SchemaSchemaDep(BaseModel):
    parent_schema: str
    child_schema: str
