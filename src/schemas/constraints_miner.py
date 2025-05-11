# /src/schemas/constraint.py

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from .base import HTTPMethod


class ConstraintSource(str, Enum):
    REQUEST_RESPONSE = "request_response"
    RESPONSE_PROPERTY = "response_property"
    DYNAMIC = "dynamic"


class StaticConstraint(BaseModel):
    id: str
    source: ConstraintSource = ConstraintSource.REQUEST_RESPONSE
    endpoint: str
    method: HTTPMethod
    expression: str  # e.g. "response.amount > 0"
    details: Optional[str]


class DynamicInvariant(BaseModel):
    id: str
    variables: List[str]  # e.g. ["input.limit", "size(response.data)"]
    expression: str  # e.g. "input.limit >= size(response.data)"


class UnifiedConstraint(BaseModel):
    id: str
    expression: str
    originating_ids: List[str]  # merged RBCTest + AGORA ids for traceability
