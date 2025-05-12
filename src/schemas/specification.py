# /src/schemas/specification.py

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .common import HTTPMethod, JSONPrimitive


class SchemaProperty(BaseModel):
    name: str = Field(..., description="Name of the schema property")
    type: str = Field(
        ..., description="Data type of the schema property (string, integer, etc.)"
    )
    description: Optional[str] = Field(
        None,
        description="Natural language description of the property from API documentation",
    )
    example: Optional[JSONPrimitive] = Field(
        None, description="Example value for this property from the API specification"
    )


class ResponseSchema(BaseModel):
    name: str = Field(
        ..., description="Name of the response schema (e.g., 'Flight', 'Booking')"
    )
    properties: Dict[str, SchemaProperty] = Field(
        ..., description="Map of property names to their metadata for this schema"
    )


class ParameterLocation(str, Enum):
    QUERY = "query"  # Parameter appears in the URL query string
    PATH = "path"  # Parameter is part of the URL path
    HEADER = "header"  # Parameter appears in the request headers
    COOKIE = "cookie"  # Parameter is sent as a cookie
    BODY = "body"  # Parameter is in the request body


class OperationParameter(BaseModel):
    name: str = Field(..., description="Name of the parameter")
    in_: ParameterLocation = Field(
        ...,
        alias="in",
        description="Location of the parameter (query, path, header, cookie, body)",
    )
    required: bool = Field(
        ..., description="Whether this parameter is required for the operation"
    )
    type: str = Field(
        ..., description="Data type of the parameter (string, integer, etc.)"
    )
    description: Optional[str] = Field(
        None,
        description="Natural language description of the parameter from API documentation",
    )


class APIResponse(BaseModel):
    status_code: int = Field(
        ge=100, le=599, description="HTTP status code for this response"
    )
    schema_ref: Optional[str] = Field(
        None,
        description="Reference to the schema defining this response (e.g., '#/components/schemas/Flight')",
    )
    description: Optional[str] = Field(
        None,
        description="Natural language description of this response from API documentation",
    )


class Operation(BaseModel):
    operation_id: str = Field(
        ..., description="Unique identifier for the API operation"
    )
    path: str = Field(..., description="URL path template for the API endpoint")
    method: HTTPMethod = Field(
        ..., description="HTTP method for this operation (GET, POST, etc.)"
    )
    summary: Optional[str] = Field(
        None, description="Brief summary of the operation from API documentation"
    )
    description: Optional[str] = Field(
        None, description="Detailed description of the operation from API documentation"
    )
    parameters: List[OperationParameter] = Field(
        ..., description="Parameters accepted by this operation"
    )
    responses: List[APIResponse] = Field(
        ..., description="Possible responses returned by this operation"
    )


class ParsedSpec(BaseModel):
    """Structured representation produced by *Spec Loader*."""

    title: str = Field(..., description="Title of the API from specification")
    version: str = Field(..., description="Version of the API from specification")
    operations: List[Operation] = Field(
        ..., description="List of operations defined in the API specification"
    )
    components: Dict[str, ResponseSchema] = Field(
        ...,
        description="Map of schema names to their definitions from components section",
    )
