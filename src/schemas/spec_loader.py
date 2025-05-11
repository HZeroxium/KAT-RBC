# /src/schemas/spec_loader.py

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .base import HTTPMethod, JSONPrimitive


class SchemaProperty(BaseModel):
    name: str
    type: str
    description: Optional[str]
    example: Optional[JSONPrimitive]


class ResponseSchema(BaseModel):
    name: str
    properties: Dict[str, SchemaProperty]


class ParameterLocation(str, Enum):
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"
    BODY = "body"


class OperationParameter(BaseModel):
    name: str
    in_: ParameterLocation = Field(alias="in")
    required: bool
    type: str
    description: Optional[str]


class APIResponse(BaseModel):
    status_code: int = Field(ge=100, le=599)
    schema_ref: Optional[str]  # e.g. "#/components/schemas/ChargeList"
    description: Optional[str]


class Operation(BaseModel):
    operation_id: str
    path: str
    method: HTTPMethod
    summary: Optional[str]
    description: Optional[str]
    parameters: List[OperationParameter]
    responses: List[APIResponse]


class ParsedSpec(BaseModel):
    """Structured representation produced by *Spec Loader*."""

    title: str
    version: str
    operations: List[Operation]
    components: Dict[str, ResponseSchema]
