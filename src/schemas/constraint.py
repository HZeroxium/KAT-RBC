# /src/schemas/constraint.py

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from .common import HTTPMethod


class ConstraintSource(str, Enum):
    REQUEST_RESPONSE = "request_response"  # Constraint between request and response
    RESPONSE_PROPERTY = "response_property"  # Constraint on response property
    DYNAMIC = "dynamic"  # Dynamically discovered invariant


class StaticConstraint(BaseModel):
    id: str = Field(..., description="Unique identifier for this static constraint")
    source: ConstraintSource = Field(
        default=ConstraintSource.REQUEST_RESPONSE,
        description="Source category of this constraint",
    )
    endpoint: str = Field(
        ..., description="API endpoint path this constraint applies to"
    )
    method: HTTPMethod = Field(
        ..., description="HTTP method this constraint applies to"
    )
    expression: str = Field(
        ...,
        description="Logical expression defining the constraint (e.g., 'response.amount > 0')",
    )
    details: Optional[str] = Field(
        None, description="Human-readable explanation of this constraint"
    )


class DynamicInvariant(BaseModel):
    id: str = Field(..., description="Unique identifier for this dynamic invariant")
    variables: List[str] = Field(
        ...,
        description="Variables referenced in this invariant (e.g., ['input.limit', 'size(response.data)'])",
    )
    expression: str = Field(
        ...,
        description="Logical expression defining the invariant (e.g., 'input.limit >= size(response.data)')",
    )


class UnifiedConstraint(BaseModel):
    id: str = Field(..., description="Unique identifier for this unified constraint")
    expression: str = Field(
        ..., description="Logical expression defining the unified constraint"
    )
    originating_ids: List[str] = Field(
        ...,
        description="IDs of source constraints that were merged to form this unified constraint",
    )
